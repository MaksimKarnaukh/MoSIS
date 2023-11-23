#define FMI_VERSION 2

#define CONCAT(a, b) CONCAT_(a, b)
#define CONCAT_(a, b) a ## b

#define FMI_PREFIX CONCAT(fmi, FMI_VERSION)

#if FMI_VERSION > 2
#define Component CONCAT(FMI_PREFIX, Instance)
#define ComponentEnvironment CONCAT(FMI_PREFIX, InstanceEnvironment)
#else
#define Component CONCAT(FMI_PREFIX, Component)
#define ComponentEnvironment CONCAT(FMI_PREFIX, ComponentEnvironment)
#endif
#define ValueReference CONCAT(FMI_PREFIX, ValueReference)
#if FMI_VERSION > 2
#define FMUstate CONCAT(FMI_PREFIX, FMUState)
#define Real CONCAT(FMI_PREFIX, Float64)
#define Integer CONCAT(FMI_PREFIX, Int64)
#else
#define FMUstate CONCAT(FMI_PREFIX, FMUstate)
#define Real CONCAT(FMI_PREFIX, Real)
#define Integer CONCAT(FMI_PREFIX, Integer)
#endif
#define Boolean CONCAT(FMI_PREFIX, Boolean)
#define Char CONCAT(FMI_PREFIX, Char)
#define String CONCAT(FMI_PREFIX, String)
#define Byte CONCAT(FMI_PREFIX, Byte)

#define Type CONCAT(FMI_PREFIX, Type)
#define EventInfo CONCAT(FMI_PREFIX, EventInfo)
#define CallbackFunctions CONCAT(FMI_PREFIX, CallbackFunctions)
#define CallbackAllocateMemory CONCAT(FMI_PREFIX, CallbackAllocateMemory)
#define CallbackFreeMemory CONCAT(FMI_PREFIX, CallbackFreeMemory)

#define StatusKind CONCAT(FMI_PREFIX, StatusKind)
#define Status CONCAT(FMI_PREFIX, Status)
#define OK CONCAT(FMI_PREFIX, OK)
#define Discard CONCAT(FMI_PREFIX, Discard)
#define Error CONCAT(FMI_PREFIX, Error)

#define True CONCAT(FMI_PREFIX, True)
#define False CONCAT(FMI_PREFIX, False)

// FUNCTIONS
#define GetVersion CONCAT(FMI_PREFIX, GetVersion)
#define GetTypesPlatform CONCAT(FMI_PREFIX, GetTypesPlatform)
#define SetDebugLogging CONCAT(FMI_PREFIX, SetDebugLogging)
#if FMI_VERSION > 2
#define InstantiateModelExchange CONCAT(FMI_PREFIX, InstantiateModelExchange)
#define InstantiateCoSimulation CONCAT(FMI_PREFIX, InstantiateCoSimulation)
#else
#define Instantiate CONCAT(FMI_PREFIX, Instantiate)
#endif
#define FreeInstance CONCAT(FMI_PREFIX, FreeInstance)
#define SetupExperiment CONCAT(FMI_PREFIX, SetupExperiment)
#define EnterInitializationMode CONCAT(FMI_PREFIX, EnterInitializationMode)
#define ExitInitializationMode CONCAT(FMI_PREFIX, ExitInitializationMode)
#define Terminate CONCAT(FMI_PREFIX, Terminate)
#define Reset CONCAT(FMI_PREFIX, Reset)
#if FMI_VERSION > 2
#define GetReal CONCAT(FMI_PREFIX, GetFloat64)
#define SetReal CONCAT(FMI_PREFIX, SetFloat64)
#define GetInteger CONCAT(FMI_PREFIX, GetInt64)
#define SetInteger CONCAT(FMI_PREFIX, SetInt64)
#else
#define GetReal CONCAT(FMI_PREFIX, GetReal)
#define SetReal CONCAT(FMI_PREFIX, SetReal)
#define GetInteger CONCAT(FMI_PREFIX, GetInteger)
#define SetInteger CONCAT(FMI_PREFIX, SetInteger)
#endif
#define GetBoolean CONCAT(FMI_PREFIX, GetBoolean)
#define GetString CONCAT(FMI_PREFIX, GetString)
#define SetBoolean CONCAT(FMI_PREFIX, SetBoolean)
#define SetString CONCAT(FMI_PREFIX, SetString)
#define GetFMUstate CONCAT(FMI_PREFIX, GetFMUstate)
#define SetFMUstate CONCAT(FMI_PREFIX, SetFMUstate)
#define FreeFMUstate CONCAT(FMI_PREFIX, FreeFMUstate)
#define SerializedFMUstateSize CONCAT(FMI_PREFIX, SerializedFMUstateSize)
#define SerializeFMUstate CONCAT(FMI_PREFIX, SerializeFMUstate)
#define DeSerializeFMUstate CONCAT(FMI_PREFIX, DeSerializeFMUstate)
#define GetDirectionalDerivative CONCAT(FMI_PREFIX, GetDirectionalDerivative)
#define EnterEventMode CONCAT(FMI_PREFIX, EnterEventMode)
#if FMI_VERSION > 2
#define NewDiscreteStates CONCAT(FMI_PREFIX, UpdateDiscreteStates)
#else
#define NewDiscreteStates CONCAT(FMI_PREFIX, NewDiscreteStates)
#endif
#define EnterContinuousTimeMode CONCAT(FMI_PREFIX, EnterContinuousTimeMode)
#define CompletedIntegratorStep CONCAT(FMI_PREFIX, CompletedIntegratorStep)
#define SetTime CONCAT(FMI_PREFIX, SetTime)
#define SetContinuousStates CONCAT(FMI_PREFIX, SetContinuousStates)
#if FMI_VERSION > 2
#define GetDerivatives CONCAT(FMI_PREFIX, GetContinuousStateDerivatives)
#else
#define GetDerivatives CONCAT(FMI_PREFIX, GetDerivatives)
#endif
#define GetEventIndicators CONCAT(FMI_PREFIX, GetEventIndicators)
#define GetContinuousStates CONCAT(FMI_PREFIX, GetContinuousStates)
#define GetNominalsOfContinuousStates CONCAT(FMI_PREFIX, GetNominalsOfContinuousStates)
#define SetRealInputDerivatives CONCAT(FMI_PREFIX, SetRealInputDerivatives)
#define GetRealOutputDerivatives CONCAT(FMI_PREFIX, GetRealOutputDerivatives)
#define DoStep CONCAT(FMI_PREFIX, DoStep)
#define CancelStep CONCAT(FMI_PREFIX, CancelStep)
#define GetStatus CONCAT(FMI_PREFIX, GetStatus)
#define GetRealStatus CONCAT(FMI_PREFIX, GetRealStatus)
#define GetIntegerStatus CONCAT(FMI_PREFIX, GetIntegerStatus)
#define GetBooleanStatus CONCAT(FMI_PREFIX, GetBooleanStatus)
#define GetStringStatus CONCAT(FMI_PREFIX, GetStringStatus)