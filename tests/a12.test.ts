/**
 * A12 Vector Tests
 * Load vectors and assert deep strict equality against reference outputs
 */

import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { join } from "path";
import { evaluateA12 } from "../src/a12.js";

// Load vectors with canonicalization: parse JSON deterministically
const vectorsPath = join(process.cwd(), "vectors", "a12.vectors.json");
const vectors = JSON.parse(readFileSync(vectorsPath, "utf-8"));

describe("A12 Product/Meta Placement Vectors", () => {
  it("should have test vectors", () => {
    expect(vectors.length).toBeGreaterThan(0);
  });

  vectors.forEach((vector: any, index: number) => {
    it(`should match vector ${index + 1}: ${JSON.stringify(vector.input)}`, () => {
      const result = evaluateA12(vector.input);
      // Deep strict equality check
      expect(result).toStrictEqual(vector.expected);
    });
  });
});
