#include<stdio.h>
#include "cwa_estimater.h"

int main(void){
    char buf_name[MAX_NAME];
    int com_credits;
    int rem_credits;
    float curr_cwa;
    float target_cwa;

    printf("Enter name:");
    fgets(buf_name,MAX_NAME,stdin);

    printf("Enter total completed credit:");
    scanf("%d",&com_credits);

    printf("Enter total remaining credits:");
    scanf("%d",&rem_credits);

    printf("Enter current CWA:");
    scanf("%f",&curr_cwa);

    printf("Enter target CWA:");
    scanf("%f",&target_cwa);


    Student student = init_student(
        buf_name,com_credits,rem_credits,curr_cwa,target_cwa
    );


    float fair_dist = calculate_fair_distribution(student);

    if(fair_dist == -1 || fair_dist == 0 ){
        printf("Impossible:Not realistic\n");
    }else{
        printf("Fair distribution:%.2f\n",fair_dist);
    }
    

    

    float p_score;
    int p_credit;
    printf("Enter priority score and credit:");
    scanf("%f %d",&p_score,&p_credit);

    float recalculate_fair_dist = recalculate_fair_distribution(student,p_score,p_credit);

    if(recalculate_fair_dist == -1 || recalculate_fair_dist == 0 ){
        printf("Impossible:Not realistic\n");
    }else{
        printf("Recalculated fair distribution:%.2f\n",recalculate_fair_dist);
    }
    

    destroy_object(student);

    return 0;
}