import { describe, it, expect } from 'vitest';
import { formatTimestamp, formatPressure, formatConcentration, formatDuration } from '@/utils/format';

describe('Format Utils', () => {
  describe('formatTimestamp', () => {
    it('should format Unix timestamp to readable date', () => {
      const timestamp = 1700000000; // Nov 14, 2023
      const result = formatTimestamp(timestamp);
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/); // MM/DD/YYYY format
    });

    it('should handle invalid timestamp', () => {
      const result = formatTimestamp(0);
      expect(result).toBeDefined();
    });
  });

  describe('formatPressure', () => {
    it('should format pressure with unit', () => {
      expect(formatPressure(3.45)).toBe('3.45 bar');
    });

    it('should round to 2 decimal places', () => {
      expect(formatPressure(3.456789)).toBe('3.46 bar');
    });

    it('should handle zero', () => {
      expect(formatPressure(0)).toBe('0.00 bar');
    });
  });

  describe('formatConcentration', () => {
    it('should format concentration with unit', () => {
      expect(formatConcentration(150.5)).toBe('150.50 ppm');
    });

    it('should round to 2 decimal places', () => {
      expect(formatConcentration(150.567)).toBe('150.57 ppm');
    });

    it('should handle zero', () => {
      expect(formatConcentration(0)).toBe('0.00 ppm');
    });
  });

  describe('formatDuration', () => {
    it('should format seconds to readable duration', () => {
      expect(formatDuration(3661)).toBe('1h 1m 1s'); // 1 hour, 1 minute, 1 second
    });

    it('should handle only seconds', () => {
      expect(formatDuration(45)).toBe('45s');
    });

    it('should handle only minutes', () => {
      expect(formatDuration(120)).toBe('2m 0s');
    });

    it('should handle hours', () => {
      expect(formatDuration(7200)).toBe('2h 0m 0s');
    });

    it('should handle zero', () => {
      expect(formatDuration(0)).toBe('0s');
    });
  });
});
