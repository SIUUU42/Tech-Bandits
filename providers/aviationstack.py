"""
Aviationstack API integration for live flight data.

Free tier: 100 requests/month
API docs: https://aviationstack.com/documentation
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from urllib import request, parse, error


class AviationstackClient:
    """Client for Aviationstack API."""
    
    BASE_URL = "http://api.aviationstack.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Aviationstack client.
        
        Args:
            api_key: API key (defaults to AVIATIONSTACK_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("AVIATIONSTACK_API_KEY")
        if not self.api_key:
            raise ValueError("Aviationstack API key not provided. Set AVIATIONSTACK_API_KEY environment variable.")
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Make HTTP request to Aviationstack API.
        
        Args:
            endpoint: API endpoint (e.g., 'flights')
            params: Query parameters
            
        Returns:
            JSON response as dict
            
        Raises:
            Exception: On API errors or network issues
        """
        params['access_key'] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}?{parse.urlencode(params)}"
        
        try:
            with request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if 'error' in data:
                    raise Exception(f"Aviationstack API error: {data['error']}")
                
                return data
        except error.HTTPError as e:
            raise Exception(f"HTTP error: {e.code} - {e.reason}")
        except error.URLError as e:
            raise Exception(f"Network error: {e.reason}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_flights(
        self,
        dep_iata: Optional[str] = None,
        arr_iata: Optional[str] = None,
        flight_date: Optional[str] = None,
        flight_status: Optional[str] = "scheduled",
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch flights from Aviationstack API.
        
        Args:
            dep_iata: Departure airport IATA code (e.g., 'DEL')
            arr_iata: Arrival airport IATA code (e.g., 'BOM')
            flight_date: Flight date in YYYY-MM-DD format
            flight_status: Flight status filter (scheduled, active, landed, cancelled, etc.)
            limit: Max results to return
            
        Returns:
            List of flight data dictionaries
        """
        params = {
            'limit': limit
        }
        
        if dep_iata:
            params['dep_iata'] = dep_iata
        if arr_iata:
            params['arr_iata'] = arr_iata
        if flight_date:
            params['flight_date'] = flight_date
        if flight_status:
            params['flight_status'] = flight_status
        
        response = self._make_request('flights', params)
        return response.get('data', [])
    
    def normalize_flight(self, api_flight: Dict) -> Dict:
        """
        Normalize Aviationstack flight data to internal schema.
        
        Args:
            api_flight: Raw flight data from API
            
        Returns:
            Normalized flight dictionary matching internal schema
        """
        # Extract flight info
        flight_info = api_flight.get('flight', {})
        airline_info = api_flight.get('airline', {})
        departure_info = api_flight.get('departure', {})
        arrival_info = api_flight.get('arrival', {})
        
        # Build flight ID from airline + flight number
        airline_iata = airline_info.get('iata', 'XX')
        flight_number = flight_info.get('number', '0000')
        flight_id = f"{airline_iata}{flight_number}"
        
        # Extract airport names (fallback to IATA codes)
        source = departure_info.get('airport', departure_info.get('iata', 'Unknown'))
        destination = arrival_info.get('airport', arrival_info.get('iata', 'Unknown'))
        
        # Extract airline name
        airline = airline_info.get('name', 'Unknown Airline')
        
        # Extract times
        scheduled_dep = departure_info.get('scheduled', '')
        scheduled_arr = arrival_info.get('scheduled', '')
        
        # Parse to date and time
        date = ''
        departure_time = ''
        arrival_time = ''
        
        if scheduled_dep:
            try:
                dt = datetime.fromisoformat(scheduled_dep.replace('Z', '+00:00'))
                date = dt.strftime('%Y-%m-%d')
                departure_time = dt.strftime('%H:%M')
            except:
                pass
        
        if scheduled_arr:
            try:
                dt = datetime.fromisoformat(scheduled_arr.replace('Z', '+00:00'))
                arrival_time = dt.strftime('%H:%M')
            except:
                pass
        
        # Map status
        flight_status = api_flight.get('flight_status', 'scheduled')
        status_map = {
            'scheduled': 'Active',
            'active': 'Active',
            'landed': 'Active',
            'cancelled': 'Cancelled',
            'incident': 'Cancelled',
            'diverted': 'Cancelled'
        }
        status = status_map.get(flight_status.lower(), 'Active')
        
        # Build normalized flight record
        normalized = {
            'flight_id': flight_id,
            'airline': airline,
            'source': source,
            'destination': destination,
            'date': date,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'status': status,
            
            # Optional fields - will be handled by defaults or computed
            'seats_available': None,
            'price': None,
            'fog_risk': None,
            'rain_risk': None,
            'wind_risk': None,
            'airport_congestion': None,
            'previous_flight_delay': None,
            'delay_probability': None,
            'mobility_friendly': 'YES',  # Default
            
            # API metadata
            'api_provider': 'aviationstack',
            'api_flight_key': flight_id,
            'last_updated_utc': datetime.utcnow().isoformat(),
            'raw_json': json.dumps(api_flight)
        }
        
        return normalized
    
    def fetch_and_normalize(
        self,
        dep_iata: Optional[str] = None,
        arr_iata: Optional[str] = None,
        flight_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch flights and normalize them in one call.
        
        Args:
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
            flight_date: Flight date in YYYY-MM-DD format
            limit: Max results
            
        Returns:
            List of normalized flight dictionaries
        """
        flights = self.get_flights(dep_iata, arr_iata, flight_date, limit=limit)
        return [self.normalize_flight(f) for f in flights]


# Airport IATA code mapping for Indian cities
CITY_TO_IATA = {
    'Delhi': 'DEL',
    'Mumbai': 'BOM',
    'Bangalore': 'BLR',
    'Hyderabad': 'HYD',
    'Chennai': 'MAA',
    'Kolkata': 'CCU',
    'Pune': 'PNQ',
    'Ahmedabad': 'AMD',
    'Jaipur': 'JAI',
    'Lucknow': 'LKO',
    'Kochi': 'COK',
    'Indore': 'IDR',
    'Chandigarh': 'IXC',
    'Goa': 'GOI',
    'Visakhapatnam': 'VTZ'
}

IATA_TO_CITY = {v: k for k, v in CITY_TO_IATA.items()}


def city_to_iata(city: str) -> Optional[str]:
    """Convert city name to IATA code."""
    return CITY_TO_IATA.get(city)


def iata_to_city(iata: str) -> Optional[str]:
    """Convert IATA code to city name."""
    return IATA_TO_CITY.get(iata, iata)  # Fallback to IATA if not found
