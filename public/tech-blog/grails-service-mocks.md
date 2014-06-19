###Mocking a service method within another service in Grails 2.3.4

I've been working with [Grails] recently. And one of the biggest wastes of time
I deal with is Unit and Integration testing. Now, I'm not saying Tests are a 
waste of time: If you're creating useful and meaningful tests, then you're doing
it right. If you're testing accessors and mutators... well, there's a special 
place in productivity hell that you belong. 

One of the biggest things in Grails is that they support a lot of different ways
to mock interactions wihin Unit tests. But sometimes, you want to test a service
that relies on other services. If you're really trying to just test a single 
service and just need to ignore the wired-in auxillary services, ones first thought
might be to use _[MockFor]_ or [MockDomain] or any other mock.

**For the love of God save yourself and don't do this**

You'll find yourself dealing with a lot of useless and uninformative error messages
if you do<sup>1</sup>. And I really don't recommend trying to understand the long list of 
closures and other verbose messages that appear in the stack traces. (I myself 
was playing with metaClass as well and accidently broke the JVM running on my 
machine for a little while!)

So far, in my experience, the best way to mock out a couple simple functions 
within a test is to use a stub and to affect _only_ _the_ _instance_ _of_ _the_ 
_service_ _you_ _need_ _to_. It's simple, and it's a two parter like this:

```
@TestFor(SomeService)
public class SomeServiceTests{
    def someService
    @Before
    public void setup() throws Exception {
        def mock = [
        	someMethodInWiredService: {String anyparameters, Object youmighthave -> return "mock!" }
        ] as WiredService
        someService.wiredService = mock
        //... continue on happily
    }
    ...
```

And that's it. No strange `MockFor(ClassName)` or wondering whether or not you've
restored a services `metaClass` to it's original state or anything of that nature.
To me, this is the way that makes sense to mock during an integration test. This
might not fit into your scenario, as really the reason why I'm doing this is 
because I need to essentially ignore another service. Why? I need to run this
test in the integration environment, but since this other services calls performs
a lot of other things (like sending emails for example), and I don't really want
to verify or wait for those processes to complete<sup>2</sup>, I just stub it out.




<sup>1 Ok maybe you can use it sometimes usefully, but you shouldn't be using Mocks in integration tests most of the time. The use case here is that you need to just stub out a service call during a test.</sup>
<sup>2 And the other service has it's own test that handles all of it's testing</sup>

[Grails]:http://grails.org/doc/2.3.4/guide/
[MockFor]:http://groovy.codehaus.org/gapi/groovy/mock/interceptor/MockFor.html
[MockDomain]:http://www.ibm.com/developerworks/library/j-grails10209/