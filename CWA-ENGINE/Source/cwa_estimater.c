#include<stdio.h>
#include<stdlib.h>
#include "cwa_estimater.h"


#define PUBLIC 
#define PRIVATE static

struct student{
    char*name;
    int completed_credits;
    int remaining_credits;
    float current_cwa;
    float target_cwa;
    float wa_remain;
};

PUBLIC Student init_student(char*name,int com_credit,int rem_credit,float curr_cwa,float target_cwa){
    //Allocate memory for student struct
    Student student = malloc(sizeof(struct student));
    if(!student){
        fprintf(stderr,"Allocation error\n");
        return NULL;
    }

    //Set Struct fields
    student->name = name;
    student->completed_credits = com_credit;
    student->remaining_credits = rem_credit;
    student->current_cwa = curr_cwa;
    student->target_cwa = target_cwa;

    
    return student;

}

PUBLIC float calculate_fair_distribution(const Student student){
    int total_credit_hrs = student->completed_credits + student->remaining_credits;
    float weighted_average_com = student->current_cwa * student->completed_credits;
    float final_weighted_average = (student->target_cwa) * total_credit_hrs;
    float weighted_average_remain = final_weighted_average - weighted_average_com;

    float score_dist = (weighted_average_remain )/ (student->remaining_credits);
    student->wa_remain = weighted_average_remain;

    if(score_dist > 100 || score_dist < 0){
        if(score_dist > 100){
            return -1;
        }else{
            return -2;
        }
    }

    return score_dist;
}

PUBLIC float recalculate_fair_distribution(const Student student,float total_priority_wa,int total_priority_credit){
    float local_wa_remain = student->wa_remain;
    
    float wa_diff = local_wa_remain - total_priority_wa;
    float credit_hr_diff = student->remaining_credits - total_priority_credit;
    float score_dist = (wa_diff)/ (credit_hr_diff);

    //Return 0 if score exceeds 100
    //Return -1 if score is less than 0
    if(score_dist > 100 || score_dist < 0){
        if(score_dist > 100){
            return -1;
        }else{
            return -2;
        }
    }
    
    return score_dist;
    
}

PUBLIC void destroy_object(const Student student){
    free(student);
}