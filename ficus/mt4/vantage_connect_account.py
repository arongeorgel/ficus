import os
import asyncio
from metaapi_cloud_sdk import MetaApi

# Note: for information on how to use this example code please read https://metaapi.cloud/docs/client/usingCodeExamples/
# It is recommended to create accounts with automatic broker settings detection instead,
# see real_time_streaming.py

token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MzZjN2NiNzgwNmIxMWMyNDU5MWQ3YTE4MmZmOWY2OCIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjYzNmM3Y2I3ODA2YjExYzI0NTkxZDdhMTgyZmY5ZjY4IiwiaWF0IjoxNzE2MjE3ODcwLCJleHAiOjE3MjM5OTM4NzB9.h8O0r_-FxYlqNp9rHF44VfN-BGwh9bXyBc7iNj1RTwi0QeVE9WN6IhpBTcUmA09y-VZ_YrAIvwk-zhrUI3X5EY9mZcGY37bmAJPOoFmNRolI6pme5XKKqjb00W3Km6uxFXXFq9Pjbxhk27D6r8AZeubbovI3rGUZZlQWgbVEqUAMHCZyPA2NmxtxKKoOVGKB4SBb2pBMiO45DFZaNN1b4Durt5HOU-my3i4ucQb1xvfQcu_ZTMeYZCP-FPd02svm0h_OpiBL-P4LCXH_-vFYHlhnv9fuuHV5Tjqj3p6KDHE5_92JgR8pVYPp1bjS6Ei5BOflPQriW03gkfoEjJlKtPJ_c2OUXqDyTAiITZMpMJi2K7Uew7cpBCPV6pL--t1At6tgMTzG3r8jBMCMyWvUk50889RPE4EQUztBJjudxAzoayBdIx9rYJgGuoHQwZSJawuF-Vm3CEO7KUzh5dFkG2PeyfZ9t9UlYj474Q-srz5PPI5FhmAJDx3_4wR-2X1huddDenU9hByutd9U70jClYwJcmz6YQJ1zrB0M9Bu5zQ5XFQMmiT-bwri0cQopE28DBlalWRYgYBGEO6O6nWQFbMU5cD2pvdZ2xAL9fki_eVAwbn6yQQniHfxEGVZiWsABVEuhkl0khnp8n-k0FN3RdqPo5L38d4D6eGLFaLEuRY'
login = '1133349'
password = 'ekP#a3Kp'
server_name = 'VantageInternational-Demo'
server_dat_file = 'servers.dat'


async def meta_api_synchronization():
    api = MetaApi(token)
    try:
        profiles = await api.provisioning_profile_api.get_provisioning_profiles_with_infinite_scroll_pagination()

        # create test MetaTrader account profile
        profile = None
        for item in profiles:
            if item.name == server_name:
                profile = item
                break
        if not profile:
            print('Creating account profile')
            profile = await api.provisioning_profile_api.create_provisioning_profile(
                {'name': server_name, 'version': 5, 'brokerTimezone': 'EET', 'brokerDSTSwitchTimezone': 'EET'}
            )
            await profile.upload_file('servers.dat', server_dat_file)
        if profile and profile.status == 'new':
            print('Uploading servers.dat')
            await profile.upload_file('servers.dat', server_dat_file)
        else:
            print('Account profile already created')

        # Add test MetaTrader account
        accounts = await api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
        account = None
        for item in accounts:
            if item.login == login and item.type.startswith('cloud'):
                account = item
                break
        if not account:
            print('Adding MT5 account to MetaApi')
            account = await api.metatrader_account_api.create_account(
                {
                    'name': 'Test account',
                    'login': login,
                    'password': password,
                    'server': server_name,
                    'provisioningProfileId': profile.id,
                    'magic': 0,
                }
            )
        else:
            print('MT5 account already added to MetaApi')

        #  wait until account is deployed and connected to broker
        print('Deploying account')
        await account.deploy()
        print('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        # connect to MetaApi API
        connection = account.get_streaming_connection()
        await connection.connect()

        # wait until terminal state synchronized to the local state
        print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await connection.wait_synchronized({'timeoutInSeconds': 600})

        # access local copy of terminal state
        print('Testing terminal state access')
        terminal_state = connection.terminal_state
        print('connected:', terminal_state.connected)
        print('connected to broker:', terminal_state.connected_to_broker)
        print('account information:', terminal_state.account_information)
        print('positions:', terminal_state.positions)
        print('orders:', terminal_state.orders)
        print('specifications:', terminal_state.specifications)
        print('EURUSD specification:', terminal_state.specification('EURUSD'))

        # access history storage
        history_storage = connection.history_storage
        print('deals:', history_storage.deals[-5:])
        print('history orders:', history_storage.history_orders[-5:])

        await connection.subscribe_to_market_data('EURUSD')
        print('EURUSD price:', terminal_state.price('EURUSD'))

        # trade
        print('Submitting pending order')
        try:
            result = await connection.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0)
            print('Trade successful, result code is ' + result['stringCode'])
        except Exception as err:
            print('Trade failed with error:')
            print(api.format_error(err))

        # finally, undeploy account after the test
        print('Undeploying MT5 account so that it does not consume any unwanted resources')
        await connection.close()
        await account.undeploy()

    except Exception as err:
        print(api.format_error(err))
    exit()


asyncio.run(meta_api_synchronization())
