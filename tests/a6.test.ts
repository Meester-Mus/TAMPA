/**
 * A6 Vector Tests
 * Load vectors and assert deep strict equality against reference outputs
 */

import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { join } from "path";
import { evaluateA6 } from "../src/a6.js";

// Load vectors with canonicalization: parse JSON deterministically
const vectorsPath = join(process.cwd(), "vectors", "a6.vectors.json");
const vectors = JSON.parse(readFileSync(vectorsPath, "utf-8"));

describe("A6 Routing Decision Vectors", () => {
  it("should have 10 test vectors", () => {
    expect(vectors).toHaveLength(10);
  });

  vectors.forEach((vector: any, index: number) => {
    it(`should match vector ${index + 1}: ${JSON.stringify(vector.input)}`, () => {
      const result = evaluateA6(vector.input);
      // Deep strict equality check
      expect(result).toStrictEqual(vector.expected);
    });
  });
});
