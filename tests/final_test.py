from agent import FlightDisruptionAgent

agent = FlightDisruptionAgent()

print('=== Testing with data_source=None (mimics "All" filter) ===\n')

# Test 1: With no data source filter (All)
print('Test 1: "Give me flights from Delhi to Mumbai" (with All filter)')
response, ranked = agent.run('Give me flights from Delhi to Mumbai', data_source=None)
print(f'Response: {response}')
print(f'Ranked flights: {len(ranked)}')
if ranked:
    for flight, score in ranked:
        print(f"  - {flight['flight_id']} {flight['source']} → {flight['destination']} at {flight['departure_time']} (score: {score:.3f})")

# Test 2: With afternoon preference
print('\n\nTest 2: "Flights from Delhi to Mumbai afternoon tomorrow"')
response, ranked = agent.run('Flights from Delhi to Mumbai afternoon tomorrow', data_source=None)
print(f'Response: {response}')
print(f'Ranked flights: {len(ranked)}')
if ranked:
    for flight, score in ranked:
        print(f"  - {flight['flight_id']} {flight['source']} → {flight['destination']} at {flight['departure_time']} (score: {score:.3f})")
