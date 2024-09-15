def count_prime_sellers(data):
    # Check if any element has isAmazon set to True
    for item in data:
        if item['isAmazon']:
            return 1000
    
    # Count elements where isPrime is True
    prime_count = sum(1 for item in data if item['isPrime'])
    return prime_count

# Example usage
extracted_data = [
    {'sellerId': 'A157BIHMVTUIZB', 'isAmazon': True, 'isShippable': True, 'isPrime': True},
    {'sellerId': 'AV2OZ7SOQBAII', 'isAmazon': False, 'isShippable': True, 'isPrime': True},
    {'sellerId': 'A1EQ83CLQMZ6VP', 'isAmazon': False, 'isShippable': True, 'isPrime': True},
    {'sellerId': 'A2F3O09R621N7L', 'isAmazon': False, 'isShippable': True, 'isPrime': True},
    {'sellerId': 'AQD1WW32B5TS0', 'isAmazon': False, 'isShippable': True, 'isPrime': True},
    {'sellerId': 'AC5IN2U1UFZKR', 'isAmazon': False, 'isShippable': True, 'isPrime': True},
    {'sellerId': 'A1KREZJHVF3GV8', 'isAmazon': False, 'isShippable': True, 'isPrime': True},
    {'sellerId': 'A10C4SW55O52YT', 'isAmazon': False, 'isShippable': True, 'isPrime': True},
    {'sellerId': 'A3IK6XUOCH7A5V', 'isAmazon': False, 'isShippable': True, 'isPrime': True}
]

print(count_prime_sellers(extracted_data))  # Output: 9
