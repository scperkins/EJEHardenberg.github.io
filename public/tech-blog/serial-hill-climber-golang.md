###Simple Binary Hill Climber in GoLang

I've been playing with [Go] recently and really enjoying it. But one of my problems
was that I couldn't think of what to do with all that great concurrent power. Web 
applications and servers are of course  one of the things I first thought of, but
that's basically the Hello World of Go. 

So instead, I looked through my books and spotted my copy of Josh Bongard's [How the Body Shapes the Way We Think]
that I picked up when I took his course on evolutionary robotics. Our first assignment
in that class was a serial hill climber. It was a super simple program written in
python, a couple for loops and an object. The point of which was to mutate a genome
string into the perfect fitness. 

Generations? Population Sizes? Sounds perfect for some concurrency play! So I built
<s>an entire Evolutionary Computation Kit</s> a small program to get a grip on how
channels in Go work, and on wetting my appetite for Evolutionary methods. 

Without further adieu, here's the entire Go program:
<script src="https://gist.github.com/EdgeCaseBerg/9c535f1cd71f2c2a8012.js"></script>

It's pretty simple. Here's a quick run down:

We create a simple struct to keep track of each member of the population, they
have a genome as well as a fitness (based on said genome), and they also store a 
reference to a channel. If you're unfamiliar with Go, you can [read up on them
here] or just take my word that they're like pipes in a Linux/Unix system. 

To create a child we initialize it's genome to a random binary sequence of 1's 
and 0's. Simplistic yes, but this is a toy problem. A cool feature of the way we
initialize our `Child` is that we use go routines to initialize each `Child`'s genome
concurrently; when we do this we also collect the initialized parts and feed them
back into our calculation of the fitness as it happens. There's no real reason to
do this in such a small example, but it's quite fun nonetheless.

```
func (c* Child) init(resChan * chan int) {
	c.resultChan = *resChan
	c.genome = make([]int, genomeSize)
	initilizeChannel := make(chan int, genomeSize)
	for i := 0; i < genomeSize; i++ {
		i := i //overshadow local 
		go func(){
			c.genome[i] = rand.Intn(2)
			initilizeChannel <- c.genome[i]
		}()	
	}
	//Compute initial fitness from initalization
	c.fitness = 0
	for i := 0; i < genomeSize; i++ {
		c.fitness += <- initilizeChannel
	}
}
```

The Mutate function represents our variation in the population, for this example
we're merely flipping a coin to decide whether or not we should allow a single
portion of the genomic string to change. One again, we fan out for the calculation
and send the fitness back to the owning struct in parts. The most important part
of the Mutate function though, is that it uses the internal `resultChan` channel
variable in the `Child` to send the fitness result to whoever is listening.

```
func (c* Child) Mutate() {
	doneChannel := make(chan int, genomeSize)
	for i := 0; i < genomeSize; i++ {
		i := i
		go func(){
			if rand.Intn(2) == 1 {
				c.genome[i] = rand.Intn(2)
			}
			doneChannel <- c.genome[i]
		}()
	}
	c.fitness = 0
	for i := 0; i < genomeSize; i++ {
		c.fitness += <- doneChannel
	}
	//Send fitness out
	c.resultChan <- c.fitness
}
```

Where does resultChan go? To the channel we opened in the `main` function called
`resultsChan` (name makes sense? imagine that). This channel is responsible for
figuring out which of the population is the best candidate for reproduction to
help shape the next generation of candidates. At the end each generation we mutate
the best `Child` and replace a small subset of the population with them.

It's a fun toy example, and this is by no means a Go tutorial, but I hope that this
helps inspire some ideas for people to start using Go as a language to express
inheritly concurrent operations such as genetic algorithms and other evolutionary
methods.

[Go]:http://golang.org
[How the Body Shapes the Way We Think]:http://mitpress.mit.edu/books/how-body-shapes-way-we-think
[hill climber]:http://en.wikipedia.org/wiki/Hill_climbing
[read up on them here]:https://gobyexample.com/channels