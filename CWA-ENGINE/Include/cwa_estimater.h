#ifndef ESTIMATER_H
#define ESTIMATER_H

typedef struct student *Student;
#define MAX_NAME 1024

Student init_student(char*name,int com_credit,int rem_credit,float curr_cwa,float target_cwa);
float calculate_fair_distribution(const Student student);
float recalculate_fair_distribution(const Student student,float priority_score,int priority_credit);
void destroy_object(const Student student);

#endif