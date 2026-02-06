

#(define debug-grob
   (lambda (grob)
     (pretty-print (ly:grob-basic-properties grob))))

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% RepeatExtender grob, event and engraver
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#(define (define-grob! grob-name grob-entry)
   (set! all-grob-descriptions
         (cons ((@@ (lily) completize-grob-entry)
                (cons grob-name grob-entry))
               all-grob-descriptions)))

#(define (define-event! type properties)
   (set-object-property! type
                         'music-description
                         (cdr (assq 'description properties)))
   (set! properties (assoc-set! properties 'name type))
   (set! properties (assq-remove! properties 'description))
   (hashq-set! music-name-to-property-table type properties)
   (set! music-descriptions
         (sort (cons (cons type properties)
                     music-descriptions)
               alist<?)))

#(define-event-class 'repeat-extender-event 'span-event)

#(define-event!
  'RepeatExtenderEvent
  '((description . "Signals where a repeat extender line starts and stops.")
    (types . (repeat-extender-event span-event event))))

#(define-grob!
  'RepeatExtender
  `((stencil . ,ly:line-spanner::print)
    (style . line)
    (thickness . 4.0)
    (to-barline . #t)
    (outside-staff-priority . #f)
    (arrow-width . 0.9)
    (arrow-length . 2.4)
    (bound-details . ((left . ((padding . 0)))
                      (right-broken . ((arrow . #t)))
                      (right . ((padding . 0)
                                (arrow . #t)))))
    (springs-and-rods . ,ly:spanner::set-spacing-rods)
    (minimum-length-after-break . 10)
    (layer . -2)
    (left-bound-info . ,ly:horizontal-line-spanner::calc-left-bound-info)
    (right-bound-info . ,ly:horizontal-line-spanner::calc-right-bound-info)
    (meta . ((class . Spanner)
             (interfaces . (font-interface
                            horizontal-line-spanner-interface
                            line-interface
                            outside-staff-interface
                            side-position-interface))))))

%% This is a copy of Measure_spanner_engraver
%% except it removes the logic snapping to next barline
#(define (Repeat_extender_engraver context)
  (let ((span '())
        (finished '())
        (event-start '())
        (event-stop '()))
   (make-engraver
    (listeners ((repeat-extender-event engraver event)
                (if (= START (ly:event-property event 'span-direction))
                 (set! event-start event)
                 (set! event-stop event))))
    ((process-music trans)
     (if (ly:stream-event? event-stop)
      (if (null? span)
       (ly:warning (G_ "cannot find start of repeat extender"))
       (begin
        (set! finished span)
        (ly:engraver-announce-end-grob trans finished event-start)
        (set! span '())
        (set! event-stop '()))))
     (if (ly:stream-event? event-start)
      (begin
       (set! span (ly:engraver-make-grob trans 'RepeatExtender event-start))
       (set! event-start '()))))
    ((stop-translation-timestep trans)
     (if (and (ly:spanner? span)
          (not (ly:spanner-bound span LEFT #f)))
      (ly:spanner-set-bound! span LEFT
       (ly:context-property context 'currentCommandColumn)))
     (if (ly:spanner? finished)
      (begin
       (if (not (ly:spanner-bound finished RIGHT #f))
        (ly:spanner-set-bound! finished RIGHT
         (ly:context-property context 'currentCommandColumn)))
       (set! finished '())
       (set! event-start '())
       (set! event-stop '()))))
    ((finalize trans)
      (if (and (ly:spanner? finished)
               (not (ly:spanner-bound finished RIGHT #f)))
          (set! (ly:spanner-bound finished RIGHT)
                (ly:context-property context 'currentCommandColumn)))
      (if (ly:spanner? span)
          (begin
            (ly:warning (G_ "unterminated repeat extender"))
            (ly:grob-suicide! span)))))))

startRepeatExtender = #(make-span-event 'RepeatExtenderEvent START)
stopRepeatExtender = #(make-span-event 'RepeatExtenderEvent STOP)

\layout {
  \context {
    \Global
    \grobdescriptions #all-grob-descriptions
  }
  \context {
    \Voice
    \consists #Repeat_extender_engraver
  }
  \context {
    \DrumVoice
    \consists #Repeat_extender_engraver
  }
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% set this variable to control score appearance
framedScoreLayout = \layout {
  \context {
    \Score
    proportionalNotationDuration = #1/8
    \override Score.SpacingSpanner.uniform-stretching = ##t
    \override StaffSymbol.color = #red
  }
  \context { \Staff \override BarLine.color = #blue }
  \context { \Voice \override NoteHead.color = #green }
}

#(define (moment->simpleduration moment)
   (let* ((p (ly:moment-main-numerator moment))
          (q (ly:moment-main-denominator moment)))
     (ly:make-duration (ly:intlog2 q) 0 p)))

#(define-public (string-pair? x)
  (and (string? (car x)) (string? (cdr x))))

framedContextBarLines =
#(define-music-function
  (context totaldur linewidth barlines music)
  (string? ly:duration? number-pair? string-pair? ly:music?)
  "Print framed music in @var{context} with extender line for @{totaldur} duration.

   @var{linewidth} is number pair for varying score linewidth for score and part
   @var{barlines} is string pair for specifying start and end barlines"
  (let* ((extender (moment->simpleduration
                     (ly:moment-sub
                       (ly:duration->moment totaldur)
                       (ly:make-moment 1 16))))
         (ctx (string->symbol context))
         (startbar (car barlines))
         (endbar (cdr barlines))
         (linewidth-score (car linewidth))
         (linewidth-part (cdr linewidth))
         (spanner-length-score (+ linewidth-score 10))
         (spanner-length-part (+ linewidth-part 10)))
    (define (scorefn lw grob)
      (grob-interpret-markup
        grob
        #{ \markup
           \pad-around #1
           \whiteout
           \override #'(thickness . 3)
           \override #'(box-padding . 0.5)
           % TODO pad top/bottom differently to left/right?
           % TODO pad left/right depending on barline type
           \box
           \override #'(baseline-skip . 1.0) % this is system-system spacing
           \score {
             \new #ctx { \bar #startbar #music \bar #endbar }
             \layout {
               \framedScoreLayout
               line-width = $lw
               indent = 0
               short-indent = 0
               ragged-right = ##f
               \context { \Score \remove Bar_number_engraver }
             }
           } #} ))
  #{
  \tag #'score {
    \tweak layer #2
    \tweak stencil #(lambda (grob) (scorefn linewidth-score grob))
    \tweak Y-offset #0
    r16
    \tweak minimum-length #spanner-length-score \startRepeatExtender
  }

  \tag #'part {
    \tweak layer #2
    \tweak stencil #(lambda (grob) (scorefn linewidth-part grob))
    \tweak Y-offset #0
    r16
    \tweak minimum-length #spanner-length-part \startRepeatExtender
  }

  \skip $extender
  \stopRepeatExtender
  #}))

%%% FRAMED SCORE
%%%
%%% \framedContextBarLines CONTEXT TOTALDUR LINEWIDTH BARLINES MUSIC
%%%
%%% - score is markup, completely independent
%%% - linewidth is pair for different widths in score and part
%%%
%%% shorthand functions for most common usage
framedStaff =
#(define-music-function
  (totaldur linewidth music)
  (ly:duration? number-pair? ly:music?)
  #{ \framedContextBarLines Staff #totaldur #linewidth #'("|" . "|") #music #})
framedStaffNoBarLines =
#(define-music-function
  (totaldur linewidth music)
  (ly:duration? number-pair? ly:music?)
  #{ \framedContextBarLines Staff #totaldur #linewidth #'("" . "") #music #})
framedStaffRepeat =
#(define-music-function
  (totaldur linewidth music)
  (ly:duration? number-pair? ly:music?)
  #{ \framedContextBarLines Staff #totaldur #linewidth #'(".|:" . ":|.") #music #})
framedStaffFlaredRepeat =
#(define-music-function
  (totaldur linewidth music)
  (ly:duration? number-pair? ly:music?)
  #{ \framedContextBarLines Staff #totaldur #linewidth #'("[|:" . ":|]") #music #})

%%% REPEAT EXTENDER
%%% - music stays on staff, better for transposition etc., no box
%%% - no tags for score and part
forceBarStyle =
#(define-music-function
  (style)
  (string?)
  "Force a barline style for this staff without affecting others."
  (let* ((len (string-length style))
         (first (if (> len 0) (string-ref style 0) #\nul))
         (last (if (> len 0) (string-ref style (- len 1)) #\nul))
         (vis (cond
               ((= 0 len) all-invisible)
               ((char=? first #\:) begin-of-line-invisible)
               ((char=? last #\:) end-of-line-invisible)
               (else all-visible))))
  #{
  \once \override Staff.BarLine.layer = #-2
  \once \override BreathingSign.break-visibility = #vis
  \once \override BreathingSign.break-align-symbol = #'staff-bar
  \once \override BreathingSign.kern = #3.0
  \once \override BreathingSign.hair-thickness = #1.9
  \once \override BreathingSign.thick-thickness = #6.0
  \once \override BreathingSign.outside-staff-priority = ##f
  \once \override BreathingSign.Y-offset = #0
  \once \override BreathingSign.layer = #-1
  \once \override BreathingSign.stencil =
  #(lambda (grob)
    (grob-interpret-markup grob #{
     \markup %%\translate #'(0.5 . 0)
     \override #'(thickness . 0)
     \center-align \whiteout \bar-line #style
     #}))
  \breathe #}))

repeatExtenderBarlines =
#(define-music-function
  (total barlines music)
  (ly:duration? string-pair? ly:music?)
  (let ((extend (moment->simpleduration
                 (ly:moment-sub
                  (ly:duration->moment total)
                  (ly:music-length music)))))
  #{
  \forceBarStyle #(car barlines) %% "[|:"
  #music
  \forceBarStyle #(cdr barlines) %% ":|]"
  \startRepeatExtender
  \skip #extend
  \stopRepeatExtender
  #}))
repeatExtender =
#(define-music-function
  (total music)
  (ly:duration? ly:music?)
  #{ \repeatExtenderBarlines #total #'(".|:" . ":|.") #music #})
repeatExtenderFlared =
#(define-music-function
  (total music)
  (ly:duration? ly:music?)
  #{ \repeatExtenderBarlines #total #'("[|:" . ":|]") #music #})

%%% USAGE

\score {
  \layout {
    \context {
      \Score
      \override BarNumber.break-visibility = #end-of-line-invisible
    }
    \context {
      \Staff
      \consists Duration_line_engraver
    }
  }
  \new Staff \keepWithTag #'score {
    \override Staff.BarLine.color = #red
    \repeatExtenderFlared 1*5 { e'4 f' g' a' }
    \repeat unfold 16 { c'8 }
    \framedStaffRepeat 1*4 #'(70 . 100) {
      \tempo 8=42
      \clef bass
      \time 12/32
      f16 e32 f e d g8.
      f16 e32 f e d g8.
    }
    \repeat unfold 16 { c'8 }
    R1
    \repeat unfold 16 { c'8 }
    \repeatExtenderFlared 1*5 { e'4 f' g' a' }
    \repeat unfold 16 { c'8 }
    \repeatExtenderBarlines 1*5 #'("S:" . ":||") { e'2 f' g' a' b' c'' \break }
    r2
    \repeat unfold 16 { c'8 }
    r2
    R1
    \startRepeatExtender
    \repeat unfold 12 e'4
    \stopRepeatExtender
    r2
    \startRepeatExtender
    \repeat unfold 12 e'4
    \stopRepeatExtender
    r2
    \bar "|."
  }
}

