_Constant390_OUT1 = 390;
_Product_Kp_IN1 = _Constant390_OUT1;
_Const20_OUT1 = 20;
_Product_Kd_IN1 = _Const20_OUT1;
_Product_Ki_IN1 = _Const20_OUT1;
_Integrator_zero_OUT1 = 0;
_Integrator_delayIn_IC = _Integrator_zero_OUT1;
_Integrator_delta_t_OUT1 = 0.0000000000000001;
_Integrator_multDelta_IN2 = _Integrator_delta_t_OUT1;
_Integrator_IN1 = _IN;
_Integrator_delayIn_IN1 = _Integrator_IN1;
_Integrator_delayIn_OUT1 = _Integrator_delayIn_IC;
_Integrator_multDelta_IN1 = _Integrator_delayIn_OUT1;
_Integrator_multDelta_OUT1 = _Integrator_multDelta_IN1 * _Integrator_multDelta_IN2;
_Integrator_sumState_IN1 = _Integrator_multDelta_OUT1;
_Const0_OUT1 = 0;
_Integrator_IC = _Const0_OUT1;
_Derrivator_IC = _Const0_OUT1;
_Integrator_delayState_IN1 = _Integrator_sumState_OUT1;
_Integrator_delayState_IC = _Integrator_IC;
_Integrator_delayState_OUT1 = _Integrator_delayState_IC;
_Integrator_sumState_IN2 = _Integrator_delayState_OUT1;
_Integrator_sumState_OUT1 = _Integrator_sumState_IN1 + _Integrator_sumState_IN2;
_Integrator_OUT1 = _Integrator_sumState_OUT1;
_Derrivator_delta_t_OUT1 = 0.0000000000000001;
_Derrivator_multIc_IN2 = _Derrivator_delta_t_OUT1;
_Derrivator_inv_IN1 = _Derrivator_delta_t_OUT1;
_Derrivator_multIc_IN1 = _Derrivator_IC;
_Derrivator_multIc_OUT1 = _Derrivator_multIc_IN1 * _Derrivator_multIc_IN2;
_Derrivator_neg1_IN1 = _Derrivator_multIc_OUT1;
_Derrivator_neg1_OUT1 = -_Derrivator_neg1_IN1;
_Derrivator_sum1_IN1 = _Derrivator_neg1_OUT1;
_Derrivator_IN1 = _IN;
_Derrivator_sum1_IN2 = _Derrivator_IN1;
_Derrivator_sum1_OUT1 = _Derrivator_sum1_IN1 + _Derrivator_sum1_IN2;
_Derrivator_delay_IC = _Derrivator_sum1_OUT1;
_Derrivator_delay_IN1 = _Derrivator_IN1;
_Derrivator_delay_OUT1 = _Derrivator_delay_IC;
_Derrivator_neg2_IN1 = _Derrivator_delay_OUT1;
_Derrivator_neg2_OUT1 = -_Derrivator_neg2_IN1;
_Derrivator_sum2_IN1 = _Derrivator_neg2_OUT1;
_Derrivator_sum2_IN2 = _Derrivator_IN1;
_Derrivator_sum2_OUT1 = _Derrivator_sum2_IN1 + _Derrivator_sum2_IN2;
_Derrivator_mult_IN1 = _Derrivator_sum2_OUT1;
_Derrivator_inv_OUT1 = 1/_Derrivator_inv_IN1;
_Derrivator_mult_IN2 = _Derrivator_inv_OUT1;
_Derrivator_mult_OUT1 = _Derrivator_mult_IN1 * _Derrivator_mult_IN2;
_Derrivator_OUT1 = _Derrivator_mult_OUT1;
_Product_Kd_IN2 = _Derrivator_OUT1;
_Product_Kd_OUT1 = _Product_Kd_IN1 * _Product_Kd_IN2;
_Summation_IN3 = _Product_Kd_OUT1;
_Product_Ki_IN2 = _Integrator_OUT1;
_Product_Ki_OUT1 = _Product_Ki_IN1 * _Product_Ki_IN2;
_Summation_IN2 = _Product_Ki_OUT1;
_Product_Kp_IN2 = _IN;
_Product_Kp_OUT1 = _Product_Kp_IN1 * _Product_Kp_IN2;
_Summation_IN1 = _Product_Kp_OUT1;
_Summation_OUT1 = _Summation_IN1 + _Summation_IN2 + _Summation_IN3;
_OUT = _Summation_OUT1;
