import programms.modules.ec_site_scraper as ec_site_scraper

if __name__ == "__main__":
    #url = "https://www.walmart.com/ip/Birdie-Bath-Portable-Golf-Ball-Cleaner-Ultimate-Personal-Golf-Ball-Washer/3181856204?adsRedirect=true"
    #url = 'https://www.amazon.com/Compute-Heatsink-Raspberry-Bluetooth-CM4104000/dp/B0BXCXDHC5/ref=sr_1_1_sspa?dib=eyJ2IjoiMSJ9.3pPWmhL5pCPr47hmmM0hhjhC7HiAifnzz7t961mUGjR8m20jmUmLfTqs-UhOYH9M_VFjFB8bkgBG5Q4yBlTIM_yZJXhEx89iMuEcXh7sS60t1nZV0QoRXFL09mpSJvrJi2wNgCXdaKM710DoUch2KSFm9ldFE9qmFIJjvKZZ2y7KbMo2FRHRX28U7LZekJ7Zeu_Qm1-opN3o6FWbQwmcq1Adys977PwlhboDbYgf8AY.dnRwnGbpdzVRY9_-myhjSKZykqNKC17KyngcIQyqrM0&dib_tag=se&keywords=raspberry+pi+compute+module&qid=1726920254&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1'
    url = 'https://www.ebay.com/itm/166980817075?itmmeta=01J8A3NJX41KQ4K36X7GP12X6Y&hash=item26e0d510b3:g:f3QAAOSwdDpm7PR7&itmprp=enc%3AAQAJAAAA4IGlUAWZBx1gbu%2FRwYCIK9xycDejQM2jFtXj6XQ0s2AeOkHbi8FEcD%2BzV3RmeZ21tGEaN9V08oBfNc8yKNVSg8Lt8ptPREabcExhLPRfxm3L7Boggv8gArOEkHfhmuoLGMkk28EpzV3kxy2FH4mGT2r0tK2B13TB50Yw5QfLJfESA70Wm3CjNhJmv3Wslx%2BHU7sFcgpeRNYHTEzA33OtwmDnmurq1oDz22y6pMZdgi6S3%2Bn1f53ULGf4ZxouM2nAg%2Bqk%2FgS%2FhBpIbCm0BWrBh8ipSpYBzN%2F9Ewy%2Fj5DNQSjw%7Ctkp%3ABk9SR9Ku1sPCZA'
    ec_site_scraper.scraper(url)