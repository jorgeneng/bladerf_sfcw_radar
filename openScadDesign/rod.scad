module reinforcementRod(x,y,z){
    cube([x,y,z],center = true);
}

//size of the box
box_y = 210;
box_x = 230;
box_z = 230;

//size of the arm extension
arm_ex_x = 10;
arm_ex_y = 280;
arm_ex_z = 40;

reinforcementRod(box_x+arm_ex_x*2,40,40);