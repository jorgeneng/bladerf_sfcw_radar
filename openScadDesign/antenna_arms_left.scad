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

//    translate([0,0,-ant_z/2+20]){
//        cube([ant_x,ant_y,ant_z],center = true); 
////        translate([0,0,-ant_z/2-dis_to_ground/2])
////        cube([50,10,dis_to_ground],center=true);
////        translate([0,-ant_y/2-dis_to_robot/2,0])
////        cube([50,dis_to_robot,10],center=true);
//    }
    }
}

left_arm_new();