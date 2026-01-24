/**
 * A11 Vector Tests
 * Load vectors and assert deep strict equality against reference outputs
 */

import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { join } from "path";
import { evaluateA11 } from "../src/a11.js";

// Load vectors with canonicalization: parse JSON deterministically
const vectorsPath = join(process.cwd(), "vectors", "a11.vectors.json");
const vectors = JSON.parse(readFileSync(vectorsPath, "utf-8"));

describe("A11 Oracle Stability Vectors", () => {
  it("should have at least 5 test vectors", () => {
    expect(vectors.length).toBeGreaterThanOrEqual(5);
  });

  vectors.forEach((vector: any, index: number) => {
    it(`should match vector ${index + 1}: ${JSON.stringify(vector.input)}`, () => {
      const result = evaluateA11(vector.input);
      // Deep strict equality check
      expect(result).toStrictEqual(vector.expected);
    });
  });
});
