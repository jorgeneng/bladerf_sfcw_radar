module left_arm(){
arm_x = 10;
arm_y = 150;
arm_z = 40;
arm_angle = 20;
rotate([arm_angle,0,0])
cube([arm_x, arm_y, arm_z],center=true);


short_arm_x = 10;
short_arm_y = 100;
short_arm_z = 40;

x_base = 180;
y_base = 40;
z_base = 40;

translate([0,cos(arm_angle)*arm_y/2+short_arm_y/4,sin(arm_angle)*arm_y/2])
    cube([short_arm_x, short_arm_y, short_arm_z],center=true);

translate([-x_base/2+0.1,cos(arm_angle)*arm_y/2+short_arm_y/2,sin(arm_angle)*arm_y/2])
    difference(){
        cube([x_base,y_base,z_base],center=true);
        translate([-x_base/2,0,-z_base/3])
            cube([x_base+2,y_base+2,z_base+2],center=true);
    }   

ant_z = 350;
ant_y = 240;
ant_x = 10;

color("blue") {
translate([-x_base+0.1,cos(arm_angle)*arm_y/2+short_arm_y/2,sin(arm_angle)*arm_y/2-ant_z/2+10])
cube([ant_x,ant_y,ant_z],center = true);
}
}

module right_arm(){
arm_x = 10;
arm_y = 150;
arm_z = 40;
arm_angle = 20;
rotate([arm_angle,0,0])
cube([arm_x, arm_y, arm_z],center=true);


short_arm_x = 10;
short_arm_y = 100;
short_arm_z = 40;

x_base = 180;
y_base = 40;
z_base = 40;

translate([0,cos(arm_angle)*arm_y/2+short_arm_y/4,sin(arm_angle)*arm_y/2])
    cube([short_arm_x, short_arm_y, short_arm_z],center=true);

translate([x_base/2-0.1,cos(arm_angle)*arm_y/2+short_arm_y/2,sin(arm_angle)*arm_y/2])
    difference(){
        cube([x_base,y_base,z_base],center=true);
        translate([x_base/2,0,-z_base/3])
            cube([x_base+2,y_base+2,z_base+2],center=true);
    }   

ant_z = 350;
ant_y = 240;
ant_x = 10;

color("blue") {
translate([x_base-0.1,cos(arm_angle)*arm_y/2+short_arm_y/2,sin(arm_angle)*arm_y/2-ant_z/2+10])
cube([ant_x,ant_y,ant_z],center = true);
}
}

module arm_extension(arm_x,arm_y,arm_z,rotate_angle){
    translate([0,-30,0])
    cube([60,10,60],center=true);
    rotate([rotate_angle,0,0])
    cube([arm_x, arm_y, arm_z],center=true); 
    
}
box_y = 210;
box_x = 230;
box_z = 230;
color("blue") {
//translate([box_x/2,install_position_y,-box_z/2])   
cube([box_x,box_y,box_z],center = true);
}
robot_z = 380-210;
robot_x = 400;
robot_y = 410;

color("red"){
translate([0,0,-(box_z+robot_z)/2])   
    cube([robot_x,robot_y,robot_z],center = true);
}

arm_x = 10;
arm_y = 280;
arm_z = 40;

dis = arm_y/2+60;
rotate_angle=45;
y_offset = dis*cos(rotate_angle);
z_offset = dis*sin(rotate_angle);

translate([-box_x/2,y_offset,z_offset])
    arm_extension(arm_x,arm_y,arm_z,rotate_angle);

//rotate([30,0,0])
//translate([box_x/2,box_y/2+arm_y/3,box_z/2-80])
//    arm_extension(arm_x,arm_y,arm_z);
//
//color("green"){
//translate([-box_x/2,box_y+arm_y/3,box_z/2])
//    left_arm();
//}
