#include <string.h>
#include <stdio.h>
#include <limits.h>

#include "fmi2Functions.h"

/* Inquire version numbers of header files */
const char* GetVersion() {
	return CONCAT(FMI_PREFIX, Version);
}

const char* GetTypesPlatform() {
	return CONCAT(FMI_PREFIX, TypesPlatform);
}

Status SetDebugLogging(Component c, Boolean loggingOn, size_t nCategories, const String categories[]) {
	return OK;
}


/* Creation and destruction of FMU instances and setting debug status */
Component Instantiate(String instanceName, Type fmuType, String fmuGUID, String fmuResourceLocation,
							const CallbackFunctions* functions, Boolean visible, Boolean loggingOn) {
	CBD* cbd = NULL;

	CallbackAllocateMemory cbAllocateMemory = functions->allocateMemory;
	CallbackFreeMemory cbFreeMemory = functions->freeMemory;

	cbd = (CBD*)cbAllocateMemory(1, sizeof(CBD));
	cbd->instanceName = instanceName;
	cbd->guid = fmuGUID;
	cbd->resourceLoction = fmuResourceLocation;
	cbd->cbAllocateMemory = cbAllocateMemory;
	cbd->cbFreeMemory = cbFreeMemory;
	cbd->componentEnvironment = functions->componentEnvironment;
	cbd->visible = visible;
	cbd->loggingOn = loggingOn;

	initialEquations(cbd);

	return (Component) cbd;
}

void FreeInstance(Component c) {
	CBD* cbd = (CBD*) c;
	if(!cbd) return;

	cbd->cbFreeMemory(cbd);
}


/* Enter and exit initialization mode, terminate and reset */
Status SetupExperiment(Component c, Boolean toleranceDefined, Real tolerance,
								Real startTime, Boolean stopTimeDefined, Real stopTime) {
	CBD* cbd = (CBD*) c;
	cbd->time = startTime;
	cbd->time_last = startTime;
	return OK;
}

Status EnterInitializationMode(Component c) {
	CBD* cbd = (CBD*) c;
	return OK;
}

Status ExitInitializationMode(Component c) {
	CBD* cbd = (CBD*) c;

	// Currently only Model Exchange mode
	cbd->isNewEventIteration = False;

	return OK;
}

Status Terminate(Component c) {
	return OK;
}

Status Reset(Component c) {
	CBD* cbd = (CBD*) c;
	initialEquations(cbd);
	return OK;
}


/* Getting and setting variable values */
Status GetReal(Component c, const ValueReference vr[], size_t nvr, Real value[]) {
	CBD* cbd = (CBD*) c;
	for(int i = 0; i < nvr; ++i) {
		value[i] = cbd->modelData[vr[i]];
	}
	return OK;
}

Status GetInteger(Component c, const ValueReference vr[], size_t nvr, Integer value[]) {
	// Integers are implicitly converted to numbers in the CBD sim.
	return Error;
}

Status GetBoolean(Component c, const ValueReference vr[], size_t nvr, Boolean value[]) {
	// Booleans are implicitly converted to numbers in the CBD sim.
	return Error;
}

Status GetString(Component c, const ValueReference vr[], size_t nvr, String value[]) {
	// Strings can/should not be used as signals in CBDs!
	return Error;
}

Status SetReal(Component c, const ValueReference vr[], size_t nvr, const Real value[]) {
	CBD* cbd = (CBD*) c;
	for(int i = 0; i < nvr; ++i) {
		cbd->modelData[vr[i]] = value[i];
	}
	return OK;
}

Status SetInteger(Component c, const ValueReference vr[], size_t nvr, const Integer value[]) {
	// Integers are implicitly converted to numbers in the CBD sim.
	return Error;
}

Status SetBoolean(Component c, const ValueReference vr[], size_t nvr, const Boolean value[]) {
	// Booleans are implicitly converted to numbers in the CBD sim.
	return Error;
}

Status SetString(Component c, const ValueReference vr[], size_t nvr, const String  value[]) {
	// Strings can/should not be used as signals in CBDs!
	return Error;
}


/* Getting and setting the internal FMU state */
Status GetFMUstate(Component c, FMUstate* fmu_state) {
	CBD* cbd = (CBD*) c;
	Real data[M];
	for(int i = 0; i < M; ++i) {
		data[i] = cbd->modelData[i];
	}
	*fmu_state = data;
	return OK;
}

Status SetFMUstate(Component c, FMUstate fmu_state) {
	CBD* cbd = (CBD*) c;
	for(int i = 0; i < M; ++i) {
		cbd->modelData[i] = *(((Real*) fmu_state) + i);
	}
	return OK;
}

Status FreeFMUstate(Component c, FMUstate* fmu_state){
	CBD* cbd = (CBD*) c;
	cbd->cbFreeMemory(fmu_state);
	fmu_state = NULL;
	return OK;
}

Status SerializedFMUstateSize(Component c, FMUstate fmu_state, size_t* size) {
	*size = M * sizeof(Real);
	return OK;
}

Status SerializeFMUstate(Component c, FMUstate fmu_state, Byte serializedState[], size_t size) {
	union {
		Real f;
		unsigned int u;
	} a;

	size_t sz = sizeof(Real);

	for(int i = 0; i < M; ++i) {
		a.f = *(((Real*) fmu_state) + i);
		for(int j = 0; j < sz; ++j) {
			serializedState[j + i * size] = a.u >> ((sz - j - 1) * CHAR_BIT);
		}
	}
	return OK;
}

Status DeSerializeFMUstate(Component c, const Byte serializedState[], size_t size, FMUstate* fmu_state) {
	union {
		Real f;
		unsigned int u;
	} a;

	size_t sz = sizeof(Real);
	Real data[M];

	a.u = 0;
	int j = 0;
	for(int i = 0; i < size; ++i) {
		a.u |= serializedState[i];
		if((i + 1) % sz == 0) {
			data[j] = a.f;
			++j;
			a.u = 0;
		} else {
			a.u = a.u << CHAR_BIT;
		}
	}

	*fmu_state = data;
	return OK;
}

/* Getting partial derivatives */
Status GetDirectionalDerivative(Component c, const ValueReference vUnknown_ref[], size_t nUnknown,
											const ValueReference vKnown_ref[], size_t nKnown,
											const Real dvKnown[], Real dvUnknown[]) {
	// Not implemented/supported
	return Error;
}


/***************************************************
Types for Functions for FMI for Model Exchange
****************************************************/

/* Enter and exit the different modes */
Status EnterEventMode(Component c) {
	CBD* cbd = (CBD*) c;
	cbd->isNewEventIteration = True;
	return OK;
}

Status NewDiscreteStates(Component c, EventInfo* eventInfo) {
	CBD* cbd = (CBD*) c;
	cbd->newDiscreteStatesNeeded = False;
	cbd->terminateSimulation = False;
	cbd->nominalsOfContinuousStatesChanged = False;
	cbd->valuesOfContinuousStatesChanged = False;

	stateEvent(cbd);
	cbd->isNewEventIteration = False;

	// Update event information
	eventInfo->newDiscreteStatesNeeded = cbd->newDiscreteStatesNeeded;
	eventInfo->terminateSimulation = cbd->terminateSimulation;
	eventInfo->nominalsOfContinuousStatesChanged = cbd->nominalsOfContinuousStatesChanged;
	eventInfo->valuesOfContinuousStatesChanged = cbd->valuesOfContinuousStatesChanged;
	eventInfo->nextEventTimeDefined = cbd->nextEventTimeDefined;
	eventInfo->nextEventTime = cbd->nextEventTime;

	return OK;
}

Status EnterContinuousTimeMode(Component c) {
	CBD* cbd = (CBD*) c;
	return OK;
}

Status CompletedIntegratorStep(Component c, Boolean noSetFMUStatePriorToCurrentPoint, Boolean* enterEventMode,
										Boolean* terminateSimulation) {
	CBD* cbd = (CBD*) c;
	*enterEventMode = False;
	*terminateSimulation = False;
	return OK;
}

/* Providing independent variables and re-initialization of caching */
Status SetTime(Component c, Real time) {
	CBD* cbd = (CBD*) c;
	cbd->time = time;
	return OK;
}

Status SetContinuousStates(Component c, const Real x[], size_t nx) {
	CBD* cbd = (CBD*) c;
	setContinuousStates(cbd, x, nx);
	cbd->valuesOfContinuousStatesChanged = True;
	return OK;
}

/* Evaluation of the model equations */
Status GetDerivatives(Component c, Real derivatives[], size_t nx) {
	CBD* cbd = (CBD*) c;
	getDerivatives(cbd, derivatives, nx);
	return OK;
}

Status GetEventIndicators(Component c, Real eventIndicators[], size_t ni) {
	// State Event Location w.r.t. 0
	return OK;
}

Status GetContinuousStates(Component c, Real x[], size_t nx) {
	CBD* cbd = (CBD*) c;
	getContinuousStates(cbd, x, nx);
	return OK;
}

Status GetNominalsOfContinuousStates(Component c, Real x_nominal[], size_t nx) {
	for(int i = 0; i < nx; ++i) {
		x_nominal[i] = 1;
	}
	return OK;
}


/***************************************************
Types for Functions for FMI for Co-Simulation
****************************************************/

/* Simulating the slave */
Status SetRealInputDerivatives(Component c, const ValueReference vr[], size_t nvr,
										const Integer order[], const Real value[]) {
	// Cannot interpolate inputs
	return Error;
}

Status GetRealOutputDerivatives(Component c, const ValueReference vr[], size_t nvr,
										const Integer order[], Real value[]) {
	for(int i = 0; i < nvr; ++i) {
		value[i] = 0;
	}
	// Cannot compute output derivatives
	return Error;
}

Status DoStep(Component c, Real currentCommunicationPoint, Real communicationStepSize,
						Boolean noSetFMUStatePriorToCurrentPoint) {
	CBD* cbd = (CBD*) c;
	if (communicationStepSize <= 0) {
		return Error;
	}
	return doStep(cbd, currentCommunicationPoint, currentCommunicationPoint + communicationStepSize);
}

Status CancelStep(Component c) {
	// Cannot cancel step
	return Error;
}

// TODO!!!
Status GetStatus(Component c, const StatusKind s, Status* value) {
	return Discard;
}

Status GetRealStatus(Component c, const StatusKind s, Real* value) {
	return Discard;
}

Status GetIntegerStatus(Component c, const StatusKind s, Integer* value) {
	return Discard;
}

Status GetBooleanStatus(Component c, const StatusKind s, Boolean* value) {
	return Discard;
}

Status GetStringStatus(Component c, const StatusKind s, String* value) {
	return Discard;
}
