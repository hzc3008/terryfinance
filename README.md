# Terry Finance

Terry Finance is an educational web app adapted from C$50 Finance. It provides users with a platform to practice stock trading using virtual money. Every new user is granted $10,000 Terry Bucks to start their trading journey. The app is accessible at [http://hzc3008.pythonanywhere.com/](http://hzc3008.pythonanywhere.com/).

The stock prices, quotes, and all price-related data are fetched using the IEX API to ensure accuracy.

The website is hosted on PythonAnywhere to minimize costs.

## Technologies

The app utilizes the Flask framework in Python, HTML, and CSS for the front-end, and connects to a SQLite database for storing data. Passwords are not stored directly in the database; they are encrypted for added security.

## Features

The app offers the following features through different routes:

1. **Login**: Login is required to access most pages. Upon successful login, the app records the user's session to prevent the need for repeated logins. Users can create an account through the /register route.
2. **Index**: This page displays two tables. The first table shows the account's total stock value, cash value, and grand total. The second table shows a breakdown of the user's inventory by each stock, including share amount, current price, FIFO cost (calculated in app.py), daily change, and total value.
3. **Quote**: Users can search for stock prices by entering a stock symbol. The app will display the current stock price, company name, and other relevant information.
4. **Buy**: This feature allows users to purchase stocks by entering a stock symbol and the number of shares they want to buy. The app will calculate the total cost and update the user's portfolio and cash balance accordingly.
5. **Sell**: Users can sell their stocks by selecting a stock symbol from their portfolio and specifying the number of shares to sell. The app will update the portfolio and cash balance based on the transaction.
6. **History**: This page displays a transaction history for the user, showing all buy and sell transactions, including the stock symbol, number of shares, price, total value, and timestamp.

## Getting Started

Visit [Terry Finance](http://hzc3008.pythonanywhere.com/) and register an account to start practicing stock trading in a risk-free environment.
