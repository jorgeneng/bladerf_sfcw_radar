module left_arm_new(){
    arm_x = 10;
    arm_y = 250;
    arm_z = 40;
    
    cube([arm_x,arm_y,arm_z],center=true);  
   
    x_base = 180;
    y_base = 50;
    z_base = 50; 
    
    translate([-x_base/2+arm_x/2+0.1,arm_y/2-y_base/2,0]){
    difference(){
        cube([x_base,y_base,z_base],center=true);
        translate([-x_base/2,0,-z_base/3])
            cube([x_base+2,y_base+2,z_base+2],center=true);
    }  
    ant_z = 350;
    ant_y = 240;
    ant_x = 10;
    
    dis_to_ground = 210;
    dis_to_robot = 300;

    translate([0,0,-ant_z/2+20]){
        cube([ant_x,ant_y,ant_z],center = true); 
//        translate([0,0,-ant_z/2-dis_to_ground/2])
//        cube([50,10,dis_to_ground],center=true);
//        translate([0,-ant_y/2-dis_to_robot/2,0])
//        cube([50,dis_to_robot,10],center=true);
    }
    }
}

module left_arm(){
arm_x = 10;
arm_y = 150;
arm_z = 40;
arm_angle = 20;
color("red"){
rotate([arm_angle,0,0])
cube([arm_x, arm_y, arm_z],center=true);
}

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
    
dis_to_ground = 200;
dis_to_robot = 300;

translate([-x_base+0.1,cos(arm_angle)*arm_y/2+short_arm_y/2,sin(arm_angle)*arm_y/2-ant_z/2+10]){
    cube([ant_x,ant_y,ant_z],center = true); 
    translate([0,0,-ant_z/2-dis_to_ground/2])
    cube([50,10,dis_to_ground],center=true);
    translate([0,-ant_y/2-dis_to_robot/2,0])
    cube([50,dis_to_robot,10],center=true);
    }
}


module right_arm_new(){
    arm_x = 10;
    arm_y = 250;
    arm_z = 40;
    
    cube([arm_x,arm_y,arm_z],center=true);  
   
    x_base = 180;
    y_base = 50;
    z_base = 50; 
    
    translate([x_base/2-arm_x/2+0.1,arm_y/2-y_base/2,0]){
    difference(){
        cube([x_base,y_base,z_base],center=true);
        translate([x_base/2,0,-z_base/3])
            cube([x_base+2,y_base+2,z_base+2],center=true);
    }  
    ant_z = 350;
    ant_y = 240;
    ant_x = 10;
    
    dis_to_ground = 210;
    dis_to_robot = 300;

    translate([0,0,-ant_z/2+20]){
        cube([ant_x,ant_y,ant_z],center = true); 
//        translate([0,0,-ant_z/2-dis_to_ground/2])
//        cube([50,10,dis_to_ground],center=true);
//        translate([0,-ant_y/2-dis_to_robot/2,0])
//        cube([50,dis_to_robot,10],center=true);
    }
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

module arm_extension_left(arm_x,arm_y,arm_z,attachLength,rotate_angle){
    y_tran = -(arm_y/2-attachLength)*cos(rotate_angle);
    z_tran = -(arm_y/2-attachLength)*sin(rotate_angle)-arm_z/2/cos(rotate_angle);
    translate([20,y_tran+5,z_tran-10])
    cube([80,10,arm_z/cos(rotate_angle)*2+20],center=true);
    rotate([rotate_angle,0,0])
    cube([arm_x, arm_y, arm_z],center=true); 
    
}

module arm_extension_right(arm_x,arm_y,arm_z,attachLength,rotate_angle){
    y_tran = -(arm_y/2-attachLength)*cos(rotate_angle);
    z_tran = -(arm_y/2-attachLength)*sin(rotate_angle)-arm_z/2/cos(rotate_angle);
    translate([-20,y_tran+5,z_tran-10])
    cube([80,10,arm_z/cos(rotate_angle)*2+20],center=true);
    rotate([rotate_angle,0,0])
    cube([arm_x, arm_y, arm_z],center=true); 
    
}

module reinforcementRod(x,y,z){
    cube([x,y,z],center = true);
}
//create the box
box_y = 210;
box_x = 230;
box_z = 230;
color("blue") {
//translate([box_x/2,install_position_y,-box_z/2])   
cube([box_x,box_y,box_z],center = true);
}

//create the robot
robot_z = 380-210;
robot_x = 400;
robot_y = 410;

color("red"){
translate([0,0,-(box_z+robot_z)/2])   
    cube([robot_x,robot_y,robot_z],center = true);
}

//create the ground
color("yellow"){
translate([0,0,-(box_z/2)-robot_z-1])
    cube([1000,1000,1],center=true);
}

//size of the arm extension
arm_ex_x = 10;
arm_ex_y = 280;
arm_ex_z = 40;
//the length of arm extension attaced on the box
attachLength = 50;
z_lift = 20;
//the angle between the arm extension and the box
rotate_angle=40;

y_offset = (box_y/2/cos(rotate_angle)-attachLength+arm_ex_y/2)*cos(rotate_angle);
z_offset = (box_y/2/cos(rotate_angle)-attachLength+arm_ex_y/2)*sin(rotate_angle)+z_lift;

translate([-box_x/2-arm_ex_x/2,y_offset,z_offset])
    arm_extension_left(arm_ex_x,arm_ex_y,arm_ex_z,attachLength,rotate_angle);

translate([-box_x/2-arm_ex_x/2-arm_ex_x,box_y+arm_ex_y/1.8,box_z/2+130])
    left_arm_new();

translate([box_x/2+arm_ex_x/2,y_offset,z_offset])
    arm_extension_right(arm_ex_x,arm_ex_y,arm_ex_z,attachLength,rotate_angle);

translate([box_x/2+arm_ex_x/2+arm_ex_x,box_y+arm_ex_y/1.8,box_z/2+130]){
    right_arm_new();
    translate([-box_x/2-arm_ex_x*1.5,0,0])
    reinforcementRod(box_x+arm_ex_x*2,40,40);
}
    

