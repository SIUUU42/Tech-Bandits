from sql_generator import SQLQueryBuilder
from datetime import datetime, timedelta

builder = SQLQueryBuilder()

print('=== Testing search logic ===\n')

# Test 1: Basic search Delhi to Mumbai
print('1. Search: Delhi to Mumbai (no date filter)')
results = builder.search_flights(source='Delhi', destination='Mumbai')
print(f'   Found: {len(results)} flights')
if results:
    for r in results[:3]:
        print(f"   - {r['flight_id']} at {r['departure_time']} ({r['status']})")

# Test 2: With today's date
print('\n2. Search: Delhi to Mumbai on 2026-02-22 (today)')
results = builder.search_flights(source='Delhi', destination='Mumbai', date='2026-02-22')
print(f'   Found: {len(results)} flights')
if results:
    for r in results[:3]:
        print(f"   - {r['flight_id']} at {r['departure_time']} ({r['status']})")

# Test 3: With tomorrow's date
print('\n3. Search: Delhi to Mumbai on 2026-02-23 (tomorrow)')
results = builder.search_flights(source='Delhi', destination='Mumbai', date='2026-02-23')
print(f'   Found: {len(results)} flights')
if results:
    for r in results[:3]:
        print(f"   - {r['flight_id']} at {r['departure_time']} ({r['status']})")

# Test 4: With time window
print('\n4. Search: Delhi to Mumbai with afternoon window (12:00-18:00)')
results = builder.search_flights(source='Delhi', destination='Mumbai', departure_window=('12:00', '18:00'))
print(f'   Found: {len(results)} flights')
if results:
    for r in results[:3]:
        print(f"   - {r['flight_id']} at {r['departure_time']} ({r['status']})")

# Test 5: Agent intent extraction
print('\n5. Testing agent intent extraction:')
from agent import FlightDisruptionAgent
agent = FlightDisruptionAgent()
state = agent.intent_extractor('Give me flights from Delhi to Mumbai')
print(f'   Intent: {state["intent"]}')
print(f'   Search params: {state["search_params"]}')

# Test 6: Full agent flow
print('\n6. Testing full agent flow:')
agent_state = agent.db_query_node(state)
print(f'   Results: {len(agent_state["query_results"])} flights')
if agent_state['response']:
    print(f'   Response: {agent_state["response"]}')
