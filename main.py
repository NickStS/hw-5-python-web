import aiohttp
import json
import sys
import datetime
import asyncio


class CurrencyClient:

    def __init__(self, base_url):
        self.base_url = base_url

    async def get_currency_rates(self, date):
        params = {
            'date': date,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        return json.loads(await response.text())
                    else:
                        raise Exception('Error getting currency rates: {}'.format(response.status))
        except aiohttp.ClientError as e:
            raise Exception('AIOHTTP ClientError: {}'.format(e))
        except json.JSONDecodeError as e:
            raise Exception('JSON decoding error: {}'.format(e))
        except Exception as e:
            raise Exception('An error occurred: {}'.format(e))

    async def get_eur_usd_rates(self, days):
        if days > 10:
            days = 10

        rates = []

        for i in range(days):
            date = (datetime.date.today() - datetime.timedelta(days=i)).strftime('%d.%m.%Y')
            try:
                currency_rates = await self.get_currency_rates(date)
                if currency_rates:
                    eur_rate = next((rate for rate in currency_rates['exchangeRate'] if rate['currency'] == 'EUR'), None)
                    usd_rate = next((rate for rate in currency_rates['exchangeRate'] if rate['currency'] == 'USD'), None)
                    rates.append({
                        date: {
                            'EUR': {
                                'sale': eur_rate['saleRate'],
                                'purchase': eur_rate['purchaseRate']
                            },
                            'USD': {
                                'sale': usd_rate['saleRate'],
                                'purchase': usd_rate['purchaseRate']
                            }
                        }
                    })
            except Exception as e:
                print('Error fetching rates for {}: {}'.format(date, e))

        return rates


async def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_days>")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("Invalid number of days. Please enter an integer.")
        sys.exit(1)

    if days <= 0:
        print("Number of days must be a positive integer.")
        sys.exit(1)

    client = CurrencyClient('https://api.privatbank.ua/p24api/exchange_rates')
    rates = await client.get_eur_usd_rates(days)

    try:
        with open('rates.json', 'w') as f:
            json.dump(rates, f, indent=4)
    except RuntimeError as e:
        print('Data saved in rates.json')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print('Data saved in rates.json')
