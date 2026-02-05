\version "2.24.4"
\include "./frame-engraver/package.ly"
#(set-global-staff-size 15)
#(set-default-paper-size "letter" 'landscape)
date = #(strftime "%Y-%m-%d" (localtime (current-time)))
\header {
    composer = \markup {
        \override #'(font-name . "DINish Bold") "María Dolores A. Matienzo"
        \vspace #-2
    }
    title = \markup { \override #'(font-name . "DINish Italic Heavy") "flagday" }
    subtitle = \markup {
        \override #'(font-name . "DINish Regular")
        \column {
            \center-align {
                \line {
                    \override #'(font-name . "DINish Italic SemiBold")
                    \italic "(a particular kind of perceptiveness)"
                }
                \smaller {
                    \override #'(font-name . "DINish Medium")
                    \line \italic { "for 4 or more piezoelectric buzzers" }
                }
                \vspace #0.5
                \line {
                    \override #'(font-name . "DINish SemiBold")
                    \small  "(5'00\" ~ 20'00\")"}
                \vspace #0.5
                \line {
                    \override #'(font-name . "DINish Regular Italic")
                    \normal-text \smaller \italic
                    "Piezoelectric buzzers should sound at irregular intervals during the piece's duration as if they were ringtones."
                }
                \vspace #0.5
            }
        }
    }
    tagline = ##f
    copyright = \markup {
        \vspace #1
        \override #'(font-name . "DINish Bold Small-Caps")
        \smallCaps "© & ℗ 2026 Imprecision Art (ASCAP)"
    }
}
\layout {
    \context {
        \Global
        \grobdescriptions #all-grob-descriptions
    }
    \context {
        \Staff
        \override VerticalAxisGroup.staff-staff-spacing.minimum-distance = #22
    }
    \context {
        \Score
        \override SystemStartBar.stencil = ##f
    }
    \context {
        \Voice
        \consists \frameEngraver
        \override FrameBracket.no-bracket = ##t
    }
}
\paper {
    page-count = 1
    % system-system-spacing.stretchability = #12
    top-margin = 0.375\in
    bottom-margin = 0.375\in
    left-margin = 0.375\in
    right-margin = 0.375\in
    ragged-right = ##f
    property-defaults.fonts.sans = "DINish Regular"
    property-defaults.fonts.typewriter = "Cascadia Code"
}
