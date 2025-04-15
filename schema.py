COVERAGE_OUTPUT_SCHEMA = {
  "type": "object",
  "name": "BusinessAutoCoverage",
  "description": "Business Auto Coverage Schema",
  "properties": {
    "liabilityInsuranceLimit": { "type": "number" },
    "liabilityInsuranceSymbol": { "type": "number" },
    "medicalPaymentsLimit": { "type": "number" },
    "medicalPaymentsSymbol": { "type": "number" },
    "uninsuredMotoristLimit": { "type": "number" },
    "uninsuredMotoristSymbol": { "type": "number" },
    "underinsuredMotoristLimit": { "type": "number" },
    "underinsuredMotoristSymbol": { "type": "number" },
    "personalInjuryProtectionLimit": { "type": "number" },
    "personalInjuryProtectionSymbol": { "type": "number" },
    "hiredAutoLimit": { "type": "number" },
    "hiredAutoSymbol": { "type": "number" },
    "nonOwnedAutoLiabilityLimit": { "type": "number" },
    "nonOwnedAutoLiabilitySymbol": { "type": "number" },
    "collisionLimit": { "type": "number" },
    "collisionDeductible": { "type": "number" },
    "comprehensiveLimit": { "type": "number" },
    "comprehensiveDeductible": { "type": "number" }
  },
  "additionalProperties": False
}

DRIVER_SCHEDULE_OUTPUT_SCHEMA = {
  "type": "object",
  "name": "DriverSchedule",
  "description": "Driver Schedule Schema",
  "properties": {
    "drivers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "fullName": { "type": "string" },
          "dateOfBirth": { "type": "string", "format": "date" },
          "licenseNumber": { "type": "string" }
        },
        "required": ["fullName", "dateOfBirth", "driversLicenseNumber"]
      }
    }
  },
  "additionalProperties": False
}
VEHICLE_SCHEDULE_OUTPUT_SCHEMA = {
  "type": "object",
  "name": "VehicleSchedule",
  "description": "Vehicle Schedule Schema",
  "properties": {
    "vehicles": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "year": { "type": "string" },
          "make": { "type": "string" },
          "model": { "type": "string" },
          "vin": { "type": "string" },
          "vehicleCost": { "type": ["number", "null"] },
          "vehiclePremium": { "type": ["number", "null"] }
        },
        "required": ["year", "make", "model", "vin"]
      }
    }
  },
  "additionalProperties": False
}

EVALUATION_OUTPUT_SCHEMA = {
  "type": "object",
  "name": "Evaluation",
  "description": "Evaluation Schema",
  "properties": {
    "score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "issues": {
      "type": "array",
      "items": { "type": "string" }
    },
    "summary": { "type": "string" }
  },
  "additionalProperties": False
}

REFINEMENT_OUTPUT_SCHEMA = {
  "type": "object",
  "name": "RefinementSuggestions",
  "description": "Refinement Suggestions Schema",
  "properties": {
    "suggestions": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "additionalProperties": False
}