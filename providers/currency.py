"""
Currency provider for transfer value conversions and market analysis.
Integrates with ExchangeRate-API for real-time currency conversions.
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class CurrencyProvider:
    """Currency provider for transfer value conversions and market analysis."""
    
    def __init__(self):
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.timeout = 10
        
        # Common football transfer currencies
        self.football_currencies = {
            "EUR": "Euro",
            "GBP": "British Pound",
            "USD": "US Dollar",
            "BRL": "Brazilian Real",
            "ARS": "Argentine Peso",
            "MXN": "Mexican Peso",
            "JPY": "Japanese Yen",
            "CNY": "Chinese Yuan",
            "RUB": "Russian Ruble",
            "TRY": "Turkish Lira"
        }
        
        # Historical transfer records for context
        self.transfer_records = {
            "highest_transfer": {"player": "Neymar", "amount": 222000000, "currency": "EUR", "year": 2017},
            "highest_english": {"player": "Jack Grealish", "amount": 117000000, "currency": "GBP", "year": 2021},
            "highest_spanish": {"player": "Eden Hazard", "amount": 115000000, "currency": "EUR", "year": 2019}
        }
    
    def convert_transfer_fee(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Convert transfer fee between currencies."""
        
        if not self.api_key:
            return {"error": "ExchangeRate API key not configured"}
        
        try:
            # Get exchange rate
            exchange_rate = self._get_exchange_rate(from_currency, to_currency)
            if not exchange_rate:
                return {"error": f"Could not get exchange rate for {from_currency} to {to_currency}"}
            
            # Convert amount
            converted_amount = amount * exchange_rate
            
            # Get market context
            market_context = self._get_market_context(converted_amount, to_currency)
            
            return {
                "original_amount": amount,
                "original_currency": from_currency,
                "converted_amount": round(converted_amount, 2),
                "converted_currency": to_currency,
                "exchange_rate": exchange_rate,
                "conversion_date": datetime.now().isoformat(),
                "market_context": market_context
            }
            
        except Exception as e:
            return {"error": f"Currency conversion error: {str(e)}"}
    
    def get_market_trends(self) -> Dict[str, Any]:
        """Get transfer market trends and analysis."""
        
        if not self.api_key:
            return {"error": "ExchangeRate API key not configured"}
        
        try:
            # Get current rates for major currencies
            major_currencies = ["EUR", "GBP", "USD"]
            current_rates = {}
            
            for currency in major_currencies:
                rate = self._get_exchange_rate("EUR", currency)
                if rate:
                    current_rates[currency] = rate
            
            # Analyze market trends
            trends = self._analyze_market_trends(current_rates)
            
            return {
                "current_rates": current_rates,
                "trends": trends,
                "market_analysis": self._get_market_analysis(trends),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Market trends error: {str(e)}"}
    
    def compare_transfer_values(self, transfers: List[Dict[str, Any]], target_currency: str = "EUR") -> Dict[str, Any]:
        """Compare multiple transfer values in a common currency."""
        
        if not self.api_key:
            return {"error": "ExchangeRate API key not configured"}
        
        try:
            compared_transfers = []
            
            for transfer in transfers:
                amount = transfer.get("amount", 0)
                currency = transfer.get("currency", "EUR")
                
                if currency == target_currency:
                    converted_amount = amount
                else:
                    exchange_rate = self._get_exchange_rate(currency, target_currency)
                    if exchange_rate:
                        converted_amount = amount * exchange_rate
                    else:
                        converted_amount = amount
                
                compared_transfers.append({
                    "player": transfer.get("player", "Unknown"),
                    "original_amount": amount,
                    "original_currency": currency,
                    "converted_amount": round(converted_amount, 2),
                    "converted_currency": target_currency,
                    "year": transfer.get("year", "Unknown")
                })
            
            # Sort by converted amount
            compared_transfers.sort(key=lambda x: x["converted_amount"], reverse=True)
            
            return {
                "transfers": compared_transfers,
                "target_currency": target_currency,
                "total_transfers": len(compared_transfers),
                "highest_value": compared_transfers[0] if compared_transfers else None,
                "lowest_value": compared_transfers[-1] if compared_transfers else None,
                "average_value": sum(t["converted_amount"] for t in compared_transfers) / len(compared_transfers) if compared_transfers else 0
            }
            
        except Exception as e:
            return {"error": f"Transfer comparison error: {str(e)}"}
    
    def get_currency_impact(self, transfer_amount: float, currency: str) -> Dict[str, Any]:
        """Analyze the impact of currency fluctuations on transfer values."""
        
        if not self.api_key:
            return {"error": "ExchangeRate API key not configured"}
        
        try:
            # Get current rate vs EUR (base currency)
            current_rate = self._get_exchange_rate("EUR", currency)
            if not current_rate:
                return {"error": f"Could not get exchange rate for {currency}"}
            
            # Calculate impact scenarios
            scenarios = {
                "current": {
                    "rate": current_rate,
                    "amount": transfer_amount,
                    "description": "Current market conditions"
                },
                "stronger": {
                    "rate": current_rate * 1.1,  # 10% stronger
                    "amount": transfer_amount * 1.1,
                    "description": "If currency strengthens by 10%"
                },
                "weaker": {
                    "rate": current_rate * 0.9,  # 10% weaker
                    "amount": transfer_amount * 0.9,
                    "description": "If currency weakens by 10%"
                }
            }
            
            return {
                "transfer_amount": transfer_amount,
                "currency": currency,
                "scenarios": scenarios,
                "volatility_risk": self._assess_volatility_risk(currency),
                "recommendation": self._get_currency_recommendation(scenarios)
            }
            
        except Exception as e:
            return {"error": f"Currency impact analysis error: {str(e)}"}
    
    def _get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get exchange rate between two currencies."""
        
        try:
            url = f"{self.base_url}/{self.api_key}/pair/{from_currency}/{to_currency}"
            
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            if data.get("result") == "success":
                return data.get("conversion_rate")
            
            return None
            
        except Exception as e:
            print(f"Exchange rate API error: {e}")
            return None
    
    def _get_market_context(self, amount: float, currency: str) -> Dict[str, Any]:
        """Get market context for a transfer amount."""
        
        # Convert to EUR for comparison
        if currency != "EUR":
            eur_rate = self._get_exchange_rate(currency, "EUR")
            if eur_rate:
                eur_amount = amount * eur_rate
            else:
                eur_amount = amount
        else:
            eur_amount = amount
        
        # Compare with historical records
        context = {
            "amount_eur": round(eur_amount, 2),
            "currency": currency,
            "market_position": self._get_market_position(eur_amount),
            "historical_comparison": self._compare_with_records(eur_amount),
            "market_tier": self._get_market_tier(eur_amount)
        }
        
        return context
    
    def _get_market_position(self, amount_eur: float) -> str:
        """Get market position for transfer amount."""
        
        if amount_eur >= 100000000:  # 100M+
            return "World record territory"
        elif amount_eur >= 50000000:  # 50M+
            return "Elite level transfer"
        elif amount_eur >= 20000000:  # 20M+
            return "High-value transfer"
        elif amount_eur >= 10000000:  # 10M+
            return "Significant transfer"
        elif amount_eur >= 5000000:  # 5M+
            return "Moderate transfer"
        else:
            return "Standard transfer"
    
    def _compare_with_records(self, amount_eur: float) -> Dict[str, Any]:
        """Compare with historical transfer records."""
        
        highest = self.transfer_records["highest_transfer"]["amount"]
        
        return {
            "percentage_of_record": round((amount_eur / highest) * 100, 1),
            "record_holder": self.transfer_records["highest_transfer"]["player"],
            "record_amount": highest,
            "record_year": self.transfer_records["highest_transfer"]["year"]
        }
    
    def _get_market_tier(self, amount_eur: float) -> str:
        """Get market tier for transfer amount."""
        
        if amount_eur >= 100000000:
            return "S+ (World Class)"
        elif amount_eur >= 50000000:
            return "S (Elite)"
        elif amount_eur >= 20000000:
            return "A (High)"
        elif amount_eur >= 10000000:
            return "B (Good)"
        elif amount_eur >= 5000000:
            return "C (Average)"
        else:
            return "D (Low)"
    
    def _analyze_market_trends(self, rates: Dict[str, float]) -> Dict[str, Any]:
        """Analyze market trends from exchange rates."""
        
        # Simple trend analysis (in production, use historical data)
        trends = {}
        
        for currency, rate in rates.items():
            if currency == "EUR":
                continue
            
            # Simulate trend analysis (in production, compare with historical data)
            if rate > 1.0:
                trends[currency] = {
                    "trend": "strengthening",
                    "strength": "moderate",
                    "impact": "positive for {currency} transfers".format(currency=currency)
                }
            else:
                trends[currency] = {
                    "trend": "weakening",
                    "strength": "moderate",
                    "impact": "negative for {currency} transfers".format(currency=currency)
                }
        
        return trends
    
    def _get_market_analysis(self, trends: Dict[str, Any]) -> str:
        """Get market analysis based on trends."""
        
        if not trends:
            return "Market data unavailable"
        
        strong_currencies = [curr for curr, trend in trends.items() if trend["trend"] == "strengthening"]
        weak_currencies = [curr for curr, trend in trends.items() if trend["trend"] == "weakening"]
        
        if len(strong_currencies) > len(weak_currencies):
            return "Overall market shows currency strengthening, favorable for international transfers"
        elif len(weak_currencies) > len(strong_currencies):
            return "Overall market shows currency weakening, challenging for international transfers"
        else:
            return "Market shows mixed trends, currency impact varies by region"
    
    def _assess_volatility_risk(self, currency: str) -> str:
        """Assess volatility risk for a currency."""
        
        # Simplified risk assessment (in production, use historical volatility data)
        high_risk_currencies = ["TRY", "RUB", "ARS", "MXN"]
        medium_risk_currencies = ["BRL", "JPY", "CNY"]
        
        if currency in high_risk_currencies:
            return "High volatility risk"
        elif currency in medium_risk_currencies:
            return "Medium volatility risk"
        else:
            return "Low volatility risk"
    
    def _get_currency_recommendation(self, scenarios: Dict[str, Any]) -> str:
        """Get currency recommendation based on scenarios."""
        
        current = scenarios["current"]["amount"]
        stronger = scenarios["stronger"]["amount"]
        weaker = scenarios["weaker"]["amount"]
        
        volatility = abs(stronger - weaker) / current
        
        if volatility > 0.2:
            return "High currency risk - consider hedging strategies"
        elif volatility > 0.1:
            return "Medium currency risk - monitor market conditions"
        else:
            return "Low currency risk - stable market conditions"

# Global currency provider instance
currency_provider = CurrencyProvider()
