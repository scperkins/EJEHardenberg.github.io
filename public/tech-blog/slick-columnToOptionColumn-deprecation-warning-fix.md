### Slick 3.1.1 warning when using nullable foreign key

Today while I was working with [Slick] I stumbled onto a deprecation warning
and had a short adventure through the documentation trying to figure out how 
to remove said warning and do what I was doing the right way. 

The warning itself was like this:

    [warn] /Path/To/Thing.scala:37: method columnToOptionColumn in trait API is deprecated: Use an explicit conversion to an Option column with `.?`
    [warn]     lazy val defaultUnitIdFk = foreignKey("fk_my_exciting_fk_constraintname", defaultUnitId, UnitTable.Unit)(u => u.unitId, onUpdate = ForeignKeyAction.SetNull, onDelete = ForeignKeyAction.SetNull)
    [warn]  

Where the `defaultUnitId` column was defined as

    val defaultUnitId: Rep[Option[Int]] = column[Option[Int]]("default_unit_id", O.Default(None))

in a `Table` class, and the foreign key this column pointed to was in another 
`Table` that had the id defined as

     val unitId: Rep[Int] = column[Int]("unit_id", O.AutoInc, O.PrimaryKey)
     
Hindsight is twenty twent, so of course looking at this now I realize the 
difference between the two types and why the implicit was being called. 
However, it didn't click for me until I saw the definition of the 
[`foreignKey` method here]. You'll note the types of the inputs, namely
that the `sourceColumns: P` and `targetColumns: (TT) ⇒ P`. The reason the
implicit was being called was because my `P` was `Rep[Option[Int]]` but 
the `Table` that the `unitId` was defined in was `Rep[Int]`. Obvious right?

So, how do you fix this? Simple, call the `.?` explicitly like so:

    lazy val defaultUnitIdFk = foreignKey("fk_my_exciting_fk_constraintname", defaultUnitId, UnitTable.Unit)(u => u.unitId.?, onUpdate = ForeignKeyAction.SetNull, onDelete = ForeignKeyAction.SetNull)

Where the only change is `u => u.unitId.?` instead of `u => u.unitId`. 

While this may seem obvious having just had it explained, if all you have
to go on is the `^` in the warning from sbt pointing to the _end_ of the 
statement. It's hard to determine _what_ in that statement was the source
of the problem that caused an implicit. 

[Slick]:http://slick.lightbend.com/doc/3.1.1/schemas.html#constraints
[`foreignKey` method here]:http://slick.lightbend.com/doc/3.1.1/api/index.html#slick.profile.RelationalTableComponent$Table@foreignKey[P,PU,TT<:AbstractTable[_],U](String,P,TableQuery[TT])((TT)⇒P,ForeignKeyAction,ForeignKeyAction)(Shape[_<:FlatShapeLevel,TT,U,_],Shape[_<:FlatShapeLevel,P,PU,_]):ForeignKeyQuery[TT,U]
