#  Drakkar-Software trading-backend
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import ccxt

import trading_backend.exchanges as exchanges
import trading_backend.errors


class Binance(exchanges.Exchange):
    SPOT_ID = "T9698EB7"
    MARGIN_ID = None
    FUTURE_ID = "uquVg2pc"

    @classmethod
    def get_name(cls):
        return 'binance'

    def _get_order_custom_id(self):
        return f"x-{self._get_id()}"

    def get_orders_parameters(self, params=None) -> dict:
        params = super().get_orders_parameters(params)
        params.update({'newClientOrderId': self._get_order_custom_id()})
        return params

    async def is_valid_account(self) -> (bool, str):
        try:
            details = await self._exchange.connector.client.sapi_get_apireferral_ifnewuser(
                params=self._exchange._get_params({
                    "apiAgentCode": self._get_id()
                })
            )
            if not details.get("rebateWorking", False):
                return False, "This account has a referral code, which is incompatible"
            if not details.get("ifNewUser", False):
                return False, "This account is not new, which is incompatible"
        except ccxt.InvalidNonce as err:
            raise trading_backend.errors.TimeSyncError(err)
        except AttributeError:
            return False, "Invalid request parameters"
        except ccxt.ExchangeError as err:
            raise trading_backend.errors.ExchangeAuthError(err)
        return True, None
