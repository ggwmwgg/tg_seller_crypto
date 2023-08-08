## Simple Seller Telegram Bot (Aiogram)

### Description
Simple Aiogram bot for sales automations. Accepts LTC payments, main currency is USD. Program architecture:
- ```data``` - ```/config.py``` - main configuration file (from .env)
- ```handlers``` - all handlers for bot (will be explained below)
- ```keyboards``` - all keyboards for bot (divided by ```inline``` and ```default```)
- ```middlewares``` = all middlewares for bot (```cf_bug_fix.py``` - fixes bug with ```callback_data```, ```throttling.py``` - simple throttling, ```watcher``` - auto-registration and ban check before main handlers)
- ```states``` - all states for bot (admin/user)
- ```utils``` - all utils for bot (with db) (will be explained below)
- ```app.py``` - main file for bot
- ```loader.py``` - Bot object and Dispatcher object with MemoryStorage

```handlers```:
- ```errors/error_handler.py``` - error handler for all kinds of errors
- ```/users/admin.py``` - admin handlers (except digital (products) and preorders)
- ```/users/admin_prod_orders.py``` - admin handlers for digital and preorder products
- ```/users/commands``` - all commands handlers (except ```/start```. ```/test``` creates test db entries ```/admin``` enters admin panel)
- ```/users/echo.py``` - echo handler (receives all text messages)
- ```/users/main_menu.py``` - main menu handler (except market related handlers (deposit, coupons, showcase, links, selecting country to start order (leads to ```/users/market.py```)))
- ```/users/market.py``` - market handlers (select product, create order)
- ```/users/orders.py``` - orders handlers (currently just one handler to cancel order)
- ```/users/start.py``` - start handler (```/start``` and checks for active orders)

```utils```:
- ```/dp_api/db_funcs.py``` - contains ```test_db_entries()``` that creates test db entries
- ```/db_api/db_api.py``` - contains db initialization
- ```/db_api/models.py``` - contains all db models
- ```/images``` - contains all images for products (which will be created by ```test_db_entries()```)
- ```mics/logging``` - contains logging configuration
- ```mics/throttling``` - contains throttling configuration
- ```orders/checker/main_checkers.py``` - contains ```check_pending_payments()``` ```check_paid_orders()``` ```withdrawn_orders_checker()``` every of these (infinite loops) runs on ```on_startup()``` launch (in ```app.py```) and checks for pending payments, paid orders and withdrawn orders
- ```bot_funcs.py``` - contains all bot main functions (every function has its own docstring, so please refer to them for more information)
- ```norifier.py``` - contains notifier function (function has its own docstring, so please refer to them for more information)
- ```set_bot_commands``` - contains function that sets bot commands ```on_startup()``` (in ```app.py```)
- ```wallet.py``` - contains functions with wallet (functions have own docstrings, so please refer to them for more information)

User can:
- ```/start``` - start bot (creates new wallet for deposits on first launch through ```watcher.py``` middleware)
- ```/test``` - create test db entries
- ```/admin``` - enter admin panel (if user is admin)
- in main menu:
  - select an order
  - confirm it
  - make payment (withdrawn here to main wallet after receiving the payment and creating new wallet)
  - get order 
  - apply coupon
  - see number of orders
  - deposit balance
  - click links (support, chat with manager, etc.)
  - see showcase

Admin can:
- in admin menu:
  - browse/add/delete preorders
  - browse/add/delete digital products
  - browse/add/delete coupons
  - browse/add/delete categories
  - browse/add/delete countries
  - browse/add/manage/delete users
  - browse/add/delete delivery methods

#### Technologies used:
- *Python*
- *Aiogram*
- *Aiohttp*
- *Asyncio*
- *Bitcoinlib*
- *Cryptography*
- *Redis*
- *Tortoise ORM*
- *PostgreSQL*
- *Docker*
- *Docker-compose*

#### Configuration:
- In ```env.dist``` file:
  - Change ```POSTGRES_USER``` to your PostgreSQL username.
  - Change ```POSTGRES_PASSWORD``` to your PostgreSQL password.
  - Change ```POSTGRES_DB``` to your PostgreSQL database name.
  - Change ```POSTGRES_HOST``` to your PostgreSQL host.
  - Change ```POSTGRES_PORT``` to your PostgreSQL port.
  - Change ```REDIS_HOST``` to your Redis host.
  - Change ```REDIS_PORT``` to your Redis port.
  - Change ```REDIS_PASSWORD``` to your Redis password.
  - Change ```BOT_TOKEN``` to your Telegram bot (API) token.
  - Change ```MAIN_PW``` to your main encryption password.
  - Change ```WALLET``` to your main wallet address.
  - Change ```ADMINS``` to your admins IDs.
- In ```docker-compose.yml```:
  - Change ```telegram_seller_db``` at line ```23``` to your PostgreSQL database name.
  - Change port at line ```30``` to your PostgreSQL port.
  - Change ```12345``` to your Redis port at line ```37```.
  - Change port at line ```41``` to your Redis port.
- Rename ```env.dist``` to ```.env```.
- Build the containers using ```docker-compose build```.
- Start the containers using ```docker-compose up```, you can add the ```-d``` flag to run in the background.
- To stop the containers, use ```docker-compose down```.

#### Usage:
- Use ```/test``` to create test db entries.
- Use ```/admin``` to enter admin panel after setting your Telegram ID in ```env.dist``` file.
- Use ```/start``` to start bot.

#### Contributing
Pull requests are welcome. For major changes please open an issue first.