package com.wjw;

import com.google.cloud.firestore.annotation.PropertyName;
import com.squareup.moshi.Json;

public class Course {
    @Json(name = "course_nbr")
    @PropertyName("course_nbr")
    public String courseNbr;
    public String crn;
    public String dept;
    @Json(name = "dept_course_nbr")
    @PropertyName("dept_course_nbr")
    public String deptCourseNbr;
    @Json(name = "seat_actual")
    @PropertyName("seat_actual")
    public int seatActual;
    @Json(name = "seat_capacity")
    @PropertyName("seat_capacity")
    public int seatCapacity;
    @Json(name = "seat_remaining")
    @PropertyName("seat_remaining")
    public int seatRemaining;
    public String term;
    public String title;
    @Json(name = "wl_actual")
    @PropertyName("wl_actual")
    public int wlActual;
    @Json(name = "wl_capacity")
    @PropertyName("wl_capacity")
    public int wlCapacity;
    @Json(name = "wl_remaining")
    @PropertyName("wl_remaining")
    public int wlRemaining;
}
