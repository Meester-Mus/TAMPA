/**
 * A6 Routing Decision Module
 * Deterministic priority lane selection based on signal strength and priority
 */

export interface A6Input {
  signal_strength: number;
  priority: "high" | "medium" | "low";
  source: "internal" | "external";
}

export interface A6Decision {
  decision: "priority_lane_1" | "priority_lane_2" | "priority_lane_3";
  confidence: number;
  thresholds_id: string;
}

/**
 * Evaluate A6 routing decision with strict priority lane selection
 * Deterministic function based on priority levels with thresholds_id
 */
export function evaluateA6(input: A6Input): A6Decision {
  const { signal_strength, priority } = input;
  
  // Normalize confidence to signal_strength / 100
  const confidence = signal_strength / 100;
  
  // Strict priority-based lane selection
  let decision: A6Decision["decision"];
  
  if (priority === "high") {
    decision = "priority_lane_1";
  } else if (priority === "medium") {
    decision = "priority_lane_2";
  } else {
    decision = "priority_lane_3";
  }
  
  return {
    decision,
    confidence,
    thresholds_id: "A6-DEFAULT-v0"
  };
}
