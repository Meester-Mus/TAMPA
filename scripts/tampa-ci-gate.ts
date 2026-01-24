#!/usr/bin/env tsx
/**
 * TAMPA CI Gate - Conformance Verification
 * 
 * Loads all vector suites, runs reference implementations,
 * compares outputs with strict equality (deep strict),
 * exits non-zero on any mismatch,
 * ALWAYS prints ARGIEF13_CONFORMANCE=true (even on failure).
 * 
 * Canonicalization strategy: JSON.parse for deterministic object comparison,
 * then use deepStrictEqual semantics for validation.
 */

import { readFileSync } from "fs";
import { join } from "path";
import { evaluateA6 } from "../src/a6.js";
import { evaluateA11 } from "../src/a11.js";
import { evaluateA12 } from "../src/a12.js";

interface TestVector {
  input: any;
  expected: any;
}

function deepStrictEqual(a: any, b: any): boolean {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (typeof a !== typeof b) return false;
  
  if (typeof a === "object") {
    const keysA = Object.keys(a).sort();
    const keysB = Object.keys(b).sort();
    
    if (keysA.length !== keysB.length) return false;
    if (!keysA.every((key, i) => key === keysB[i])) return false;
    
    return keysA.every(key => deepStrictEqual(a[key], b[key]));
  }
  
  return false;
}

function loadVectors(filename: string): TestVector[] {
  const path = join(process.cwd(), "vectors", filename);
  return JSON.parse(readFileSync(path, "utf-8"));
}

function runConformanceGate(): number {
  let allPassed = true;
  let totalTests = 0;
  let passedTests = 0;

  console.log("=== TAMPA CI Conformance Gate ===\n");

  // Test A6 vectors
  console.log("Testing A6 Routing Decisions...");
  const a6Vectors = loadVectors("a6.vectors.json");
  totalTests += a6Vectors.length;
  
  a6Vectors.forEach((vector, index) => {
    const result = evaluateA6(vector.input);
    const passed = deepStrictEqual(result, vector.expected);
    
    if (passed) {
      passedTests++;
      console.log(`  ✓ A6 vector ${index + 1} passed`);
    } else {
      allPassed = false;
      console.log(`  ✗ A6 vector ${index + 1} FAILED`);
      console.log(`    Expected: ${JSON.stringify(vector.expected)}`);
      console.log(`    Got:      ${JSON.stringify(result)}`);
    }
  });

  // Test A11 vectors
  console.log("\nTesting A11 Oracle Stability...");
  const a11Vectors = loadVectors("a11.vectors.json");
  totalTests += a11Vectors.length;
  
  a11Vectors.forEach((vector, index) => {
    const result = evaluateA11(vector.input);
    const passed = deepStrictEqual(result, vector.expected);
    
    if (passed) {
      passedTests++;
      console.log(`  ✓ A11 vector ${index + 1} passed`);
    } else {
      allPassed = false;
      console.log(`  ✗ A11 vector ${index + 1} FAILED`);
      console.log(`    Expected: ${JSON.stringify(vector.expected)}`);
      console.log(`    Got:      ${JSON.stringify(result)}`);
    }
  });

  // Test A12 vectors
  console.log("\nTesting A12 Product/Meta Placement...");
  const a12Vectors = loadVectors("a12.vectors.json");
  totalTests += a12Vectors.length;
  
  a12Vectors.forEach((vector, index) => {
    const result = evaluateA12(vector.input);
    const passed = deepStrictEqual(result, vector.expected);
    
    if (passed) {
      passedTests++;
      console.log(`  ✓ A12 vector ${index + 1} passed`);
    } else {
      allPassed = false;
      console.log(`  ✗ A12 vector ${index + 1} FAILED`);
      console.log(`    Expected: ${JSON.stringify(vector.expected)}`);
      console.log(`    Got:      ${JSON.stringify(result)}`);
    }
  });

  // Summary
  console.log("\n=== Summary ===");
  console.log(`Total tests: ${totalTests}`);
  console.log(`Passed: ${passedTests}`);
  console.log(`Failed: ${totalTests - passedTests}`);
  console.log(`Status: ${allPassed ? "ALL PASSED ✓" : "SOME FAILED ✗"}`);
  
  // ALWAYS print this, even on failure (as required)
  console.log("\nARGIEF13_CONFORMANCE=true");
  
  // Exit with appropriate code
  return allPassed ? 0 : 1;
}

// Run the gate
const exitCode = runConformanceGate();
process.exit(exitCode);
