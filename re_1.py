import re

def check_pattern(pattern: str, value: str) -> bool:
    return re.match(pattern, value)

def main():
    pattern = r'^([A-Z0-9]{13,14})?$'
    value ='SELLERIDTEST01'
    print(check_pattern(pattern, value))

if __name__ == '__main__':
    main()