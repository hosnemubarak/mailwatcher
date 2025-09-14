import os
import requests

class BaseEndpoint(object):
    @staticmethod
    def call_api(notif_url, path, method: str = 'get', headers: dict = {}, params: dict = {}, body: dict = {}, timeout=30):
        '''
        Utility function to call the API.

        Args:
            path: The path of the endpint. e.g. `/nodes/` or `/nodes/13/`
            params: The parameters of the endpoint.

        Returns:
            The output of the API based on which endpoint is called.
        '''
        try:

            if method == 'get':
                res = requests.get(f'{notif_url}{path}', headers=headers, params=params, timeout=timeout)
            elif method == 'post':
                res = requests.post(f'{notif_url}{path}', headers=headers, params=params, json=body, timeout=timeout)
            elif method == 'delete':
                res = requests.delete(f'{notif_url}{path}', headers=headers, params=params, timeout=timeout)
            elif method == 'put':
                res = requests.put(f'{notif_url}{path}', headers=headers, params=params, json=body, timeout=timeout)
            else:
                raise ValueError(f"Method {method} is not supported.")

            if res.status_code == 200:
                return res.json()
            if res.status_code == 201:
                return res.json()

            print(f'Error: {res.status_code} {res.reason} [{res.text}]')
            return None
        except Exception as e:
            print(e)
            return None
