/**
 *  Main model header file.
 *  DO NOT CHANGE!
 */
#include "fmi2TypesPlatform.h"
#include "fmi2FunctionTypes.h"
#include "defs.h"

typedef void* (*AllocateMemoryFnc)(size_t nobj, size_t size);
typedef void (*FreeMemoryFnc)(void*);

typedef struct {
	Real time;
	Real time_last;

	String instanceName;
	String guid;
	String resourceLoction;
	Boolean visible;
	Boolean loggingOn;

	AllocateMemoryFnc cbAllocateMemory;
	FreeMemoryFnc cbFreeMemory;

	Real modelData[M];
	ComponentEnvironment componentEnvironment;

	// event info
	Boolean newDiscreteStatesNeeded;
	Boolean terminateSimulation;
	Boolean nominalsOfContinuousStatesChanged;
	Boolean valuesOfContinuousStatesChanged;
	Boolean nextEventTimeDefined;
	Real nextEventTime;

	Boolean isNewEventIteration;

} CBD;

void initialEquations(CBD* cbd);
void calculateEquations(CBD* cbd);

Status doStep(CBD* cbd, double t, double tNext);

void stateEvent(CBD* cbd);
void getContinuousStates(CBD* cbd, double x[], size_t nx);
void setContinuousStates(CBD* cbd, const double x[], size_t nx);
void getDerivatives(CBD* cbd, double dx[], size_t nx);
void getStateEvents(CBD* cbd, double z[], size_t nz);