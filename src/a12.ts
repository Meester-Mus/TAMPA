/**
 * A12 Product/Meta Placement and Transition Module
 * Deterministic placement checker with explicit transition logic
 */

export interface A12Input {
  product_type: "meta" | "standard";
  placement_request: "top" | "middle" | "bottom";
  transition_required: boolean;
}

export interface A12Result {
  placement: string;
  transition_allowed: boolean;
  placement_id: string;
}

/**
 * Evaluate placement and transition requirements
 * Deterministic: meta products allow transitions, standard products do not
 */
export function evaluateA12(input: A12Input): A12Result {
  const { product_type, placement_request, transition_required } = input;
  
  // Construct deterministic placement name
  const placement = `${product_type}_${placement_request}`;
  
  // Deterministic: meta products allow transitions, standard do not
  const transition_allowed = product_type === "meta" && transition_required;
  
  return {
    placement,
    transition_allowed,
    placement_id: "A12-PLACEMENT-v0"
  };
}
