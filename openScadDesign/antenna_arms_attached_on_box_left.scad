module arm_extension_left(arm_x,arm_y,arm_z,attachLength,rotate_angle){
    y_tran = -(arm_y/2-attachLength)*cos(rotate_angle);
    z_tran = -(arm_y/2-attachLength)*sin(rotate_angle)-arm_z/2/cos(rotate_angle);
    translate([20,y_tran+5,z_tran-10])
    cube([80,10,arm_z/cos(rotate_angle)*2+20],center=true);
    rotate([rotate_angle,0,0])
    cube([arm_x, arm_y, arm_z],center=true); 
    
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
arm_extension_left(arm_ex_x,arm_ex_y,arm_ex_z,attachLength,rotate_angle);