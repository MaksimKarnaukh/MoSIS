/**
 *  Main model definition file.
 *  DO NOT CHANGE!
 */

#include "version.h"
#include "model.h"
#include <stdio.h>
#include <math.h>

void initialEquations(CBD* cbd) {
    Real delta = 0.0;

	#include "eq0.c"

	cbd->time_last = cbd->time;
}

void calculateEquations(CBD* cbd) {
	Real delta = cbd->time - cbd->time_last;

	#include "eqs.c"

	cbd->time_last = cbd->time;
}

void getContinuousStates(CBD* cbd, double x[], size_t nx) {}

void setContinuousStates(CBD* cbd, const double x[], size_t nx) {}

void getDerivatives(CBD* cbd, double dx[], size_t nx) {}

void getStateEvents(CBD* cbd, double z[], size_t nz) {}

void stateEvent(CBD* cbd) {
	// No state events found
	cbd->nominalsOfContinuousStatesChanged = False;
	cbd->terminateSimulation = False;
	cbd->nextEventTimeDefined = False;
}

Status doStep(CBD* cbd, double t, double tNext) {
	// No state events found
	Boolean timeEvent;

	double h = tNext - t;
	while(cbd->time + h < tNext + 0.01 * h) {

		timeEvent = cbd->nextEventTimeDefined && cbd->time >= cbd->nextEventTime;

		if(timeEvent) {
			stateEvent(cbd);
		}

		if(cbd->terminateSimulation) {
			// Force termination
			return Discard;
		}
		cbd->time += h;
		calculateEquations(cbd);
	}

	return OK;
}

