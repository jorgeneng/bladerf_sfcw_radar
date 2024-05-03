//leave some space between antenna to the frame
margin = 10;
//dimension of the base attached to antenna
x_base = 228+margin;
y_base = 50;
z_base = 4;
//dimension of the gap on the base
x_gap = 40;
y_gap = 35;
z_gap = 5;
//dimension of the stands
x_stand = 4;
y_stand = 235;
z_stand = 40;
//radius of holes on the base
r_hole = 3;

//distance from the centers of holes to the border of base in +Y direction
d_b_1 = 6;
d_b_2 = 32;

//distance from the centers of holes to the border of base in +X direction
d_g_1 = 69+margin/2;
d_g_2 = 83+margin/2;

difference(){
    //create the base
    difference() {
    cube([x_base,y_base,z_base],center=true);
    translate([0,(y_base-y_gap)/2+0.001,0])
        cube([x_gap,y_gap,z_gap],center=true);
    }
    
    //8 holes on the base
//    translate([x_base/2-d_g_1,y_base/2-d_b_1,0])
//        cylinder(h=10,r=r_hole,center=true);
//    translate([-(x_base/2-d_g_1),y_base/2-d_b_1,0])
//        cylinder(h=10,r=r_hole,center=true);
//    translate([x_base/2-d_g_1,y_base/2-d_b_2,0])
//        cylinder(h=10,r=r_hole,center=true);
//    translate([-(x_base/2-d_g_1),y_base/2-d_b_2,0])
//        cylinder(h=10,r=r_hole,center=true);
    
    translate([x_base/2-d_g_1,y_base/2-20,0])
        cube([r_hole*2,34,10],center=true);
    translate([-(x_base/2-d_g_1),y_base/2-20,0])
        cube([r_hole*2,34,10],center=true);
    
//    translate([x_base/2-d_g_2,y_base/2-d_b_1,0])
//        cylinder(h=10,r=r_hole,center=true);
//    translate([-(x_base/2-d_g_2),y_base/2-d_b_1,0])
//        cylinder(h=10,r=r_hole,center=true);
//    translate([x_base/2-d_g_2,y_base/2-d_b_2,0])
//        cylinder(h=10,r=r_hole,center=true);
//    translate([-(x_base/2-d_g_2),y_base/2-d_b_2,0])
//        cylinder(h=10,r=r_hole,center=true);
        
    translate([x_base/2-d_g_2,y_base/2-20,0])
        cube([r_hole*2,34,10],center=true);
    translate([-(x_base/2-d_g_2),y_base/2-20,0])
        cube([r_hole*2,34,10],center=true);
}
translate([0,-160+25,0])
difference(){
    cube([x_base,30,z_base],center=true);
    translate([x_base/2-8,0,0])
        cube([r_hole*2,20,10],center=true);
    translate([-x_base/2+8,0,0])
        cube([r_hole*2,20,10],center=true);
}

//the top frame
toBaseCenter = 20;
translate([0,y_base/2+toBaseCenter,0])
difference(){
    cube([x_base,z_base,z_stand],center=true);
    translate([10,0,10])
    rotate([90,0,0])
        cylinder(h=10,r=r_hole,center=true);
    translate([10,0,-10])
    rotate([90,0,0])
        cylinder(h=10,r=r_hole,center=true);
    translate([-10,0,10])
    rotate([90,0,0])
        cylinder(h=10,r=r_hole,center=true);
    translate([-10,0,-10])
    rotate([90,0,0])
        cylinder(h=10,r=r_hole,center=true);
}

//the stand on left
translate([x_base/2 - 0.001,(y_base/2+toBaseCenter)-y_stand/2+z_base/2,0])
//translate([x_base/2 - 0.001,(y_base/2+shift)-y_stand/2+z_base/2,0])
    cube([x_stand,y_stand,z_stand],center=true);

//the stand on right
translate([-x_base/2 + 0.001,(y_base/2+toBaseCenter)-y_stand/2+z_base/2,0])
    cube([x_stand,y_stand,z_stand],center=true);

