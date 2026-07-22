echo(version=version());
$fn = 80 / 1;
e=0.01; //epsilon
//height = .765;
//paisley_width = 15;
//paisley_height = 15;
//flower_width = 10;
//flower_height = 10;
container_height = 25;

debug = false;
show_paisley = true;
show_flowers = false;
show_board = false;
show_lid = true;
show_battery = false;
battery_pack_width = 35.5;
battery_pack_height = 65;
//battery_pack_depth = 10;
battery_pack_depth = 11;
battery_pack_x_offset = battery_pack_width/2;
battery_pack_y_offset = battery_pack_height/2;
battery_clip_x_offset = battery_pack_x_offset + 1;

board_width = 27;
board_offset = board_width/2;

rotate([0,0,0]){
  translate([0,0,0])
  linear_extrude(height = 1)
    polygon(points=[[9, -46.5], [-42.5001, -46.5], [-43.3062, -46.4187], [-44.057, -46.1856], [-44.7365, -45.8168], [-45.3284, -45.3284], [-45.8168, -44.7364], [-46.1855, -44.0569], [-46.4185, -43.3061], [-46.4997, -42.5], [-46.4933, 31], [-11.4069, 31], [9, 10.5931]]);
  //stop
  translate([-32,26,0])
  cube([20, 2, 5], false);
  translate([-32,-45,0])
  cube([20, 2, 5], false);
}
//battery clips
translate([-22,-9.5,0]){
  rotate([0,0,0]){
    difference(){
      union(){
        //East clips
        //battery_clip(x, y, z, battery_pack_depth, x_rotate, y_rotate, z_rotate, show_stop, north_clip, usb_side){
        battery_clip(battery_pack_x_offset + 1.5, board_offset, 0, battery_pack_depth, 0, 0, 180, true, true, false);
        battery_clip(battery_pack_x_offset + 1.5, -board_offset, 0, battery_pack_depth, 0, 0, 180, true, false, false);
        //West clips
        battery_clip(-battery_pack_x_offset - 1.5, board_offset, 0, battery_pack_depth, 0, 0, 0, true, false, true);
        //translate([-battery_pack_x_offset-2.5, board_offset-4, 12])
        //cube([5, 4, 2], false);
        battery_clip(-battery_pack_x_offset - 1.5, -board_offset, 0, battery_pack_depth, 0, 0, 0,true,true, true);
        //translate([-battery_pack_x_offset-2.5, -board_offset, 12])
        //cube([5, 4, 2], false);
      }
      union(){
        /*
        translate([-22.3,-12.5,16])
        cube([8,4,14],center=false);
        translate([-22.3+(2.54*14),9.475,16])
        cube([3,3,10],center=false);        
        translate([-22.3+(2.54*16),9.475,16])
        cube([4,3,14],center=false);
        */

        //Large cutouts
        translate([0,0,10])
        cube([44, board_width-8, 24], true);
        translate([0,-27,10])
        cube([44, board_width-8, 24], true);
      }
    }
  }
}

module battery_clip(x, y, z, battery_pack_depth, x_rotate, y_rotate, z_rotate, show_stop, north_clip, usb_side){
  translate([x,y,z]){
    //battery clips
    clip_width = 2;
    clip_top_width = 8;
    clip_height = 8;
    clip_depth = battery_pack_depth + 3;
    clip_inside_x_offset = 4;
    clip_offset = clip_height/2;
    stop_upright_depth = 19;
    channel_depth = 9;
    rotate([x_rotate,y_rotate,z_rotate]){
      translate([0,0,0]){
        difference(){
          union(){
            //upright
            translate([-clip_width/2,-clip_offset,0])
            cube([clip_width, clip_height, clip_depth], false);
            //top
            translate([-clip_width/2,-clip_offset,clip_depth-clip_width])
            cube([clip_top_width, clip_height, clip_width], false);
            //channel
            translate([-clip_width/2,-clip_width/2,0])
            cube([clip_top_width, 2, container_height - 2], false);        
            if(show_stop){
              if(north_clip){
                //stop upright
                translate([-5,-(clip_width/2)+3,0])
                cube([8, clip_width, stop_upright_depth], false);
                if(!usb_side){
                  //stop
                  translate([-5,-(clip_width/2)+3,4])
                  cube([clip_width, clip_width, stop_upright_depth], false);
                }
              }
              else{
                //stop upright
                translate([-5,(clip_width/2)-5,0])
                cube([8, clip_width, stop_upright_depth], false);
                if(!usb_side){
                  //stop
                  translate([-5,(clip_width/2)-5,4])
                  cube([clip_width, clip_width, stop_upright_depth], false);
                }
              }
            }
          }
          union(){
            translate([-clip_width/2+clip_width,-clip_offset,0])
            cube([10, clip_height+2, clip_depth-clip_width], false);
          }
        }
      }
    }
  }
}

if(show_battery){
  translate([-battery_pack_width-4,-battery_pack_height/2 - 8,1])
  %cube([battery_pack_width, battery_pack_height, battery_pack_depth], false);
}


if(show_board){
  display_height = 4;
  frame_height = 2.5;
  board_height = .5;
  board_knockout_height = 2;
  usb_height = 2.5;
  m2_radius = 1;
  //translate([-21.5,-10,-13]){
  translate([0,2,13]){
    rotate([0,0,0]){
      difference(){
        union(){
          //board
          color("white",100)
          translate([0,0,0])
          linear_extrude(height = board_height)
          polygon(points=[[-47.85, -22.196], [-45.85, -24.196], [-0.35, -24.196], [-0.35, -20.196], [3.65, -16.196], [3.65, -6.696], [-0.35, -2.696], [-0.35, 1.304], [-45.85, 1.304], [-47.85, -0.696], [-47.85, -5.946], [-46.35, -7.446], [-46.35, -15.446], [-47.85, -16.946]]);
          //display
          color("green",100)
          translate([0,0,0])
          linear_extrude(height = display_height)
          polygon(points=[[-3.85, -2.196], [-3.85, -16.196], [-29.85, -16.196], [-29.85, -2.196]]);
          
          //display frame
          translate([0,0,0])
          linear_extrude(height = frame_height)
          polygon(points=[[-33.35, -20.696], [-0.35, -20.696], [-0.35, -2.196], [-33.35, -2.196]]);
          //usb-c connector
          color("red",100)
          translate([0,0,board_height])
          linear_extrude(height = usb_height)
          polygon(points=[[-40.85, -8.096], [-48.15, -8.096], [-48.15, -14.796], [-40.85, -14.796]]);
        }
        union(){
          translate([19.9,7.25,-1])
          cylinder(h=board_knockout_height, r=1 ,center=false);
          translate([-9.1,-7.25,-1])
          cylinder(h=board_knockout_height, r=1 ,center=false);
          translate([-9.1,7.25,-1])
          cylinder(h=board_knockout_height, r=1 ,center=false);
          translate([19.9,-7.25,-1])
          cylinder(h=board_knockout_height, r=1 ,center=false);    
        }
      }
    }
  }
}