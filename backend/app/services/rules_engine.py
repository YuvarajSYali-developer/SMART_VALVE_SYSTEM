"""
Rules Engine for Safety Validation
"""
import os
from typing import Dict, List, Tuple
from ..utils.logger import logger


class RulesEngine:
    """Validates telemetry against safety rules"""
    
    def __init__(self):
        # Load thresholds from environment or use defaults
        self.max_pressure = float(os.getenv("MAX_PRESSURE_BAR", "6.0"))
        self.critical_concentration = float(os.getenv("CRITICAL_CONCENTRATION", "500.0"))
        self.min_src_concentration = 10.0
        self.max_dst_concentration = 400.0
        
        logger.info(f"Rules Engine initialized:")
        logger.info(f"  - Max Pressure: {self.max_pressure} bar")
        logger.info(f"  - Critical Concentration: {self.critical_concentration} units")
    
    def validate_telemetry(self, telemetry: dict) -> Tuple[bool, List[str]]:
        """
        Validate telemetry against safety rules
        Returns (is_safe, list_of_violations)
        """
        violations = []
        
        # Check pressure sensors
        p1 = telemetry.get("p1", 0)
        p2 = telemetry.get("p2", 0)
        
        if p1 > self.max_pressure:
            violations.append(f"Pressure sensor 1 exceeds limit: {p1} > {self.max_pressure} bar")
        
        if p2 > self.max_pressure:
            violations.append(f"Pressure sensor 2 exceeds limit: {p2} > {self.max_pressure} bar")
        
        # Check concentration sensors
        c_src = telemetry.get("c_src", 0)
        c_dst = telemetry.get("c_dst", 0)
        
        if c_src > self.critical_concentration:
            violations.append(f"Source concentration critical: {c_src} > {self.critical_concentration} units")
        
        if c_dst > self.critical_concentration:
            violations.append(f"Destination concentration critical: {c_dst} > {self.critical_concentration} units")
        
        is_safe = len(violations) == 0
        
        if not is_safe:
            logger.warning(f"Safety violations detected: {violations}")
        
        return is_safe, violations
    
    def can_open_valve(self, telemetry: dict) -> Tuple[bool, str]:
        """
        Check if valve can be safely opened based on current telemetry
        Returns (can_open, reason)
        """
        # Check if in emergency mode
        if telemetry.get("em", 0) == 1:
            return False, "System in emergency mode"
        
        # Validate current telemetry
        is_safe, violations = self.validate_telemetry(telemetry)
        if not is_safe:
            return False, f"Safety violations: {'; '.join(violations)}"
        
        # Check source concentration
        c_src = telemetry.get("c_src", 0)
        if c_src < self.min_src_concentration:
            return False, f"Source concentration too low: {c_src} < {self.min_src_concentration}"
        
        # Check destination concentration
        c_dst = telemetry.get("c_dst", 0)
        if c_dst > self.max_dst_concentration:
            return False, f"Destination concentration too high: {c_dst} > {self.max_dst_concentration}"
        
        return True, "All checks passed"
    
    def get_alert_priority(self, violation_type: str) -> str:
        """Determine alert priority based on violation type"""
        critical_keywords = ["pressure", "critical", "emergency"]
        
        for keyword in critical_keywords:
            if keyword.lower() in violation_type.lower():
                return "CRITICAL"
        
        return "HIGH"


# Global rules engine instance
rules_engine = RulesEngine()
