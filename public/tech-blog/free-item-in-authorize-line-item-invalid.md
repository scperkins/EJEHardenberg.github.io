###Unit Price of 0 causing problems in Authorize.net CIM lineitem


Today at work I ran into an interesting problem. The problem was this: 

One of our clients has an ecommerce platform we built for them, as part of its
backend, it uses Authorize.net's [CIM service]. Today and yesterday they happened
to be running a free item. Besides the obvious server load funtimes to be troubleshot,
there was a peculiar problem popping up. If someone tried to buy the free item and
any other non-free item, the Authorize.net API would return this error message:


    The element 'lineItems' in namespace
    AnetApi/xml/v1/schema/AnetApiSchema.xsd' has invalid child element
    taxable' in namespace 'AnetApi/xml/v1/schema/AnetApiSchema.xsd'. List
    of possible elements expected: 'unitPrice' in namespace
    AnetApi/xml/v1/schema/AnetApiSchema.xsd'.

Which seemed a bit odd. Why would the taxable element be messed up? It's simply set
to false all the time. User's were checking out with the free item fine, and with
paid items fine, but when combined into multiple line items this message appeared.

Troubleshooting involved playing around locally with removing the unit price and
taxable fields entirely, getting a different error message. Good! This means that
the problem does involve those two fields. Removing the taxable field didn't change
the message, so it seemed the problem lay in the unitPrice being 0.

I checked out the [schema] from authorize and noted the following area:

    <xs:restriction base="xs:decimal">
        <xs:minInclusive value="0.00"/>
        <xs:fractionDigits value="4"/>
    </xs:restriction>

Well, I wondered, could it be that it is seeing 0 as a false value or something
other than an integer? In [this SO post] someone noted that qoutes are a good idea,
to which I tried and recieved a message about the format being invalid. So that
was out. 

Instead, I used `sprintf` to format the number into a decimal form so that Authorize's
API wouldn't treat it as whatever it had been.

Old:

    $lineItem->unitPrice = $item->price // is 0


Fixed:

    $lineItem->unitPrice   = sprintf("%.2f", $item->price);

And lo' and behold. The transaction with a mixed set of items was processed succesfully!

Hope this helps anyone out there who runs into the same problem I did. 


[CIM service]:http://developer.authorize.net/api/cim/
[schema]:https://api.authorize.net/xml/v1/schema/AnetApiSchema.xsd
[this SO post]:http://stackoverflow.com/a/14720793/1808164