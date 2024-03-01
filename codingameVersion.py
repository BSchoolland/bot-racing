import sys
import math
class Podracer():
    def __init__(self,x=0,y=0,vx=0,vy=0,angle=0,next_check_point_id=1,next_check_point_X=0,next_check_point_Y=0,memory=[],EnemyA='',EnemyB='',ally='',mission='RACER'):
        self.x=x
        self.y=y
        self.vx=vx
        self.vy=vy
        self.angle=angle
        self.next_check_point_id = next_check_point_id
        self.next_check_point_X = next_check_point_X
        self.next_check_point_Y=next_check_point_Y
        self.memory = memory
        self.EnemyA=EnemyA
        self.EnemyB=EnemyB
        self.mission = mission
        self.last_check_point_id  = next_check_point_id
        self.score = 0
        self.ally = ally
        self.interceptioncounter=30
        self.AllyTimeout=-1
        self.LastAllyScore = self.score
    def setAlly(self,ally):
        self.ally = ally
    def setAllValues(self,x=0,y=0,vx=0,vy=0,angle=0,next_check_point_id=1,next_check_point_X=0,next_check_point_Y=0,memory=[],EnemyA='',EnemyB='',ally=''):
        self.x=x
        self.y=y 
        self.vx=vx
        self.vy=vy
        self.angle=angle
        self.next_check_point_id = next_check_point_id
        self.next_check_point_X = next_check_point_X
        self.next_check_point_Y=next_check_point_Y
        self.memory = memory
        self.EnemyA=EnemyA
        self.EnemyB=EnemyB
        if self.last_check_point_id!=self.next_check_point_id:
            self.score+=1
            self.last_check_point_id=self.next_check_point_id
    def MainControl(self):
        if self.score < self.ally.score:
            self.mission = 'DEFENDER'
        elif self.score > self.ally.score:
            self.mission = 'RACER'
        elif self.score<2:
            self.mission = 'RACER'
        else:
            DistA = distanceFormula(self.x,self.y,self.next_check_point_X,self.next_check_point_Y)
            DistB = distanceFormula(self.ally.x,self.ally.y,self.ally.next_check_point_X,self.ally.next_check_point_Y)
            if DistA<DistB:
                self.mission = 'RACER'
            else:
                self.mission = 'DEFENDER'
        if self.mission == 'RACER':
            Print =self.Racer()
        else:
            Print =self.Defender()
        return(Print)
    def Defender(self):
        if self.LastAllyScore != self.ally.score:
            self.AllyTimeout = 0
            self.LastAllyScore=self.ally.score
        self.AllyTimeout+=1
        
        target = self.GetTargetEnemy()
        GoToX,GoToY,n=self.interceptBasedOnProjectedPath(target)
        bump = self.ProjectCollision('NO')[1]
        thrust = 200
        Distance = distanceFormula(self.x,self.y,target.x,target.y)
        dist = distanceFormula(self.x,self.y,GoToX,GoToY)
        thrust = 0.025*dist
        thrust =round(thrust)
        if thrust >100:
            thrust = 200
        if dist<1500:
            GoToX,GoToY=target.x,target.y
            thrust = 0
        if bump == 'BUMP':
            self.interceptioncounter=0
            GoToX,GoToY=target.x,target.y
            thrust = 'SHIELD'
        if n<10:
            GoToX,GoToY=target.x,target.y
            thrust = 200
            GoToX,GoToY=self.collideMomentum(GoToX,GoToY,target)
            GoToX,GoToY=self.StopSidewaysMomentum(GoToX,GoToY)
        elif Distance<1500:
            GoToX,GoToY=target.x,target.y
            thrust = 200
        #Save Ally from timeout
        if self.AllyTimeout>50:
            GoToX,GoToY=self.ally.x,self.ally.y
            thrust = 200
        if bump == 'BUMP':
            self.interceptioncounter=0
            GoToX,GoToY=target.x,target.y
            thrust = 'SHIELD'
        #GoToX,GoToY=self.StopSidewaysMomentum(GoToX,GoToY)
        return(str(GoToX)+' '+str(GoToY)+' '+str(thrust)+' '+self.mission)
    def collideMomentum(self,GoToX,GoToY,target):
        GoToX=GoToX-self.vx+5*target.vx
        GoToY=GoToY-self.vy+5*target.vy
        return (GoToX,GoToY)
    def GetTargetEnemy(self):
        target = ''
        if self.EnemyA.score>self.EnemyB.score:
            target=EnemyA
        elif self.EnemyA.score<self.EnemyB.score:
            target=EnemyB
        else:
            DistA = distanceFormula(EnemyA.x,EnemyA.y,EnemyA.next_check_point_X,EnemyA.next_check_point_Y)
            DistB = distanceFormula(EnemyB.x,EnemyB.y,EnemyB.next_check_point_X,EnemyB.next_check_point_Y)
            if DistA<DistB:
                target=EnemyA
            else:
                target=EnemyB
        return(target)
    def Racer(self):
        Thrust = 200
        distanceToPoint=distanceFormula(self.x,self.y,self.next_check_point_X,self.next_check_point_Y)
        
        hit,bump = self.ProjectPoint()
        thrust=200
        if hit == 'CENTERPOINT':
            n = self.next_check_point_id+1
            if n>=len(self.memory):
                n=0
            GoToX,GoToY=memory[n].split(' ')
            GoToX,GoToY=int(GoToX),int(GoToY)
            thrust=200
        elif hit =='SIDEPOINT':
            n = self.next_check_point_id+1
            if n>=len(self.memory):
                n=0
            GoToX,GoToY=memory[n].split(' ')
            GoToX,GoToY=int(GoToX),int(GoToY)
            Thrust = 0
        else:
            GoToX = self.next_check_point_X
            GoToY = self.next_check_point_Y
        AngleToGoTo = self.AngleToXY(GoToX,GoToY)
        GoToX,GoToY=self.StopSidewaysMomentum(GoToX,GoToY) #
        if Thrust==200 and abs(AngleToGoTo) < 1 and distanceToPoint>5000 and self.mission == 'RACER' and self.ally.mission == 'DEFENDER' and hit != 'BUMP' and self.score>3:
            Thrust = 'BOOST'
        if abs(AngleToGoTo)>45 and hit != 'CENTERPOINT':
            if distanceToPoint<1200:
                Thrust = 0
            elif abs(AngleToGoTo)>45:
                Thrust = 0
        elif abs(AngleToGoTo)>90:
            Thrust = 0
        if hit =='BUMP' and math.sqrt(self.vx**2+self.vy**2)>100:
            Thrust='SHIELD'
        
        return(str(GoToX)+' '+str(GoToY)+' '+str(Thrust))
    def AngleToXY(self,X,Y):
        DistanceX=(X-self.x)
        DistanceY=(Y-self.y)
        if DistanceY==0:
            DistanceY = 0.00001
        Degrees = math.atan(DistanceX/DistanceY)*180/math.pi
        Degrees += self.angle
        while Degrees>360 or Degrees<0:
            if Degrees>360:
                Degrees-=360
            else:
                Degrees+=360
        if DistanceX>0 and DistanceY>0:
            Degrees-=90
        elif DistanceX>0 and DistanceY<0:
            Degrees-=270
        elif DistanceX<0 and DistanceY>0:
            Degrees-=90
        elif DistanceX<0 and DistanceY<0:
            Degrees-=270
        return Degrees
    def VectorAngle(self,X,Y):
        DistanceX=(X)
        DistanceY=(Y)
        if DistanceY==0:
            DistanceY = 0.00001
        Degrees = math.atan(DistanceX/DistanceY)*180/math.pi
        #removed the adition of my angle
        if DistanceX>0 and DistanceY>0:
            Degrees-=90
            Degrees*=-1
        elif DistanceX<0 and DistanceY>0:
            Degrees*=-1
            Degrees+=90
        elif DistanceX<0 and DistanceY<0:
            Degrees*=-1
            Degrees+=270
        elif DistanceX>0 and DistanceY<0:
            Degrees*=-1
            Degrees+=270
        return Degrees
    def ShorterDegrees(self,currentAngle,targetAngle):
        copycurrentAngle=5*round(currentAngle/5)
        copytargetAngle=5*round(targetAngle/5)
        distancePositive=0
        while copycurrentAngle!= copytargetAngle:
            distancePositive+=5
            #print(distancePositive, file=sys.stderr, flush=True)
            copycurrentAngle+=5
            if copycurrentAngle>360:
                copycurrentAngle=0
        copycurrentAngle=round(currentAngle)
        copytargetAngle=round(targetAngle)
        distancenegative=0
        while copycurrentAngle!= copytargetAngle:
            distancenegative-=5
            copycurrentAngle-=5
            if copycurrentAngle<=0:
                copycurrentAngle=360
        if abs(distancePositive)<abs(distancenegative):
            return distancePositive
        else:
            return distancenegative
    def StopSidewaysMomentum(self,GoToX,GoToY):
        
        GoToX=GoToX-3*self.vx
        GoToY=GoToY-3*self.vy
        return GoToX,GoToY    
    
    def ResultOfCollision2(self,myX,myY,enemyX,enemyY,myVX,myVY,enemy):
        myScore = 0
        enemyScore = 0
        enemyVX,enemyVY = enemy.vx,enemy.vy
        MyDistanceFromTarget=distanceFormula(myX,myY,self.next_check_point_X,self.next_check_point_Y)
        myScore= MyDistanceFromTarget-distanceFormula(myX+enemyVX,myY+enemyVY,self.next_check_point_X,self.next_check_point_Y)

        enemyDistanceFromTarget=distanceFormula(enemyX,enemyY,enemy.next_check_point_X,enemy.next_check_point_Y)
        enemyScore= enemyDistanceFromTarget-distanceFormula(enemyX+self.vx,enemyY+self.vy,enemy.next_check_point_X,enemy.next_check_point_Y)
        #print(myScore,enemyScore, file=sys.stderr, flush=True)
        return myScore,enemyScore

    def ResultOfCollision(self,myX,myY,enemyX,enemyY,myVX,myVY,enemy):
        angle=math.tan((myX-enemyX)/(myY-enemyY))
        if (myX-enemyX)<0 and (myY-enemyY)<0:
            angle+=math.pi
        if (myX-enemyX)<0 and (myY-enemyY)>0:
            angle+=math.pi
        speed_A=math.sqrt(self.vx**2+self.vy**2)
        addedX_A = speed_A*(math.sin(angle))
        addedY_A = speed_A*(math.cos(angle))
        speed_B=math.sqrt(enemy.vx**2+enemy.vy**2)
        addedX_B = speed_B*(math.sin(angle))
        addedX_B = speed_B*(math.cos(angle))
        newVX=self.vx + addedX_A + addedX_B
        newVY=self.vx + addedX_A + addedX_B
        myscore = distanceFormula(myX+self.vx,myY+self.vy,self.next_check_point_X,self.next_check_point_Y)-distanceFormula(myX+newVX,myY+newVY,self.next_check_point_X,self.next_check_point_Y)
        print(myscore, file=sys.stderr, flush=True)
        return myscore,0
    def ProjectCollision(self,hit):
        #Will it hit enemyA? 
        oldHit=hit  
        hit2='NO'         
        myX= self.x
        myY=self.y
        EnemyAX=self.EnemyA.x
        EnemyAY = self.EnemyA.y
        EnemyBX=self.EnemyB.x
        EnemyBY = self.EnemyB.y
        EnemyCX=self.ally.x
        EnemyCY = self.ally.y
        P=100
        done = False
        n=0
        if self.mission=='RACER':
            mult=1.5
        else:
            mult=2.2
        while n < (mult*P) and not done:
            n+=1
            myX+=self.vx/P
            myY+=self.vy/P
            EnemyAX+=self.EnemyA.vx/P
            EnemyAY+=self.EnemyA.vy/P
            EnemyBX+=self.EnemyB.vx/P
            EnemyBY+=self.EnemyB.vy/P
            EnemyCX+=self.ally.vx/P
            EnemyCY+=self.ally.vy/P
            DistanceFromA = distanceFormula(myX,myY,EnemyAX,EnemyAY)
            DistanceFromB = distanceFormula(myX,myY,EnemyBX,EnemyBY)
            DistanceFromC = distanceFormula(myX,myY,EnemyCX,EnemyCY)
            if DistanceFromA < 800:
                done = True
                if self.ResultOfCollision(myX,myY,EnemyAX,EnemyAY,self.vx,self.vy,self.EnemyA)[0]<-200:
                    hit = 'BUMP'
                if self.EnemyA.ResultOfCollision(EnemyAX,EnemyAY,myX,myY,EnemyA.vx,self.vy,self)[1]<30:
                    hit2='BUMP'
            elif DistanceFromB<800:
                done = True
                if self.ResultOfCollision(myX,myY,EnemyBX,EnemyBY,self.vx,self.vy,self.EnemyB)[0]<-300:
                    hit = 'BUMP'
                if self.EnemyB.ResultOfCollision(EnemyBX,EnemyBY,myX,myY,EnemyB.vx,self.vy,self)[1]<30:
                    hit2='BUMP'
            elif DistanceFromC<800:
                done = True
                if self.ResultOfCollision(myX,myY,EnemyCX,EnemyCY,self.vx,self.vy,self.ally)[0]<-300:
                    hit = 'BUMP'
                if self.ResultOfCollision(myX,myY,EnemyCX,EnemyCY,self.vx,self.vy,self.ally)[1]>50:
                    hit2='BUMP'
        if n>150:
            hit=oldHit
        print(hit,hit2, file=sys.stderr, flush=True)
        return hit,hit2


    def ProjectPoint(self):
        X=self.x
        Y=self.y
        SpeedX = self.vx
        SpeedY = self.vy
        hit = 'AIR'
        for n in range(7):
            SpeedX*=0.85
            SpeedY*=0.85
            X+=SpeedX
            Y+=SpeedY

            DistanceFromPoint = distanceFormula(X,Y,self.next_check_point_X,self.next_check_point_Y)
            if DistanceFromPoint < 400:
                hit = 'CENTERPOINT'
            elif DistanceFromPoint<590 and hit!='CENTERPOINT':
                hit = 'SIDEPOINT'
        hit,bump = self.ProjectCollision(hit)
        return hit,bump
    def interceptBasedOnProjectedPath(self,target):
        waypoints=target.GetWaypoints()
        #print(, file=sys.stderr, flush=True)
        n=1
        SelfSpeed = 200
        GoToX,GoToY=waypoints[n].split(' ')
        GoToX,GoToY=int(GoToX),int(GoToY)
        time = distanceFormula(self.x,self.y,GoToX,GoToY)/SelfSpeed
        while time>2*n:
            n+=1
            GoToX,GoToY=waypoints[n].split(' ')
            GoToX,GoToY=int(GoToX),int(GoToY)
            time = distanceFormula(self.x,self.y,GoToX,GoToY)/SelfSpeed
        return(GoToX,GoToY,n)
    def GetWaypoints(self):
        waypoints = []
        memory = self.EnemyA.memory
        #waypoints consist of x,y 
        #later on in the progam past and future waypoints will be used 
        #to calculate the enemy's desired direction given a certain waypoint
        wayPointSread = 250#distance between waypoints
        waypoints.append(str(self.x)+' '+str(self.y))#first waypoint is the position of the racer
        n = self.next_check_point_id
        direction = 0
        for i in range(200):#start with just 10 waypoints, number will be increased after testing
            GoToX,GoToY=memory[n].split(' ')
            GoToX,GoToY=int(GoToX),int(GoToY)#the next checkpoint
            #Angle=self.AngleToXY(GoToX,GoToY)-self.angle#absolute angle to checkpoint
            
            #Angle = math.radians(abs(Angle))
            #print(math.atan(Angle), file=sys.stderr, flush=True)
            LastX,LastY=waypoints[-1].split(' ')
            LastX,LastY=int(LastX),int(LastY)#the last waypoint
            if LastX == GoToX:
                GoToX+=0.00001
            if LastY == GoToY:
                GoToY+=0.00001
            if GoToX-LastX<0 and GoToY-LastY<0:
                NextX=round(LastX-wayPointSread*abs(math.atan((GoToX-LastX)/(GoToY-LastY))))
                NextY=round(LastY-wayPointSread*abs(math.atan((GoToY-LastY)/(GoToX-LastX))))
                direction = 1
            elif GoToX-LastX<0 and GoToY-LastY>0:
                direction = 2
                NextX=round(LastX-wayPointSread*abs(math.atan((GoToX-LastX)/(GoToY-LastY))))
                NextY=round(LastY+wayPointSread*abs(math.atan((GoToY-LastY)/(GoToX-LastX))))
            elif GoToX-LastX>0 and GoToY-LastY>0:
                direction = 3
                NextX=round(LastX+wayPointSread*abs(math.atan((GoToX-LastX)/(GoToY-LastY))))
                NextY=round(LastY+wayPointSread*abs(math.atan((GoToY-LastY)/(GoToX-LastX))))
            else:
                direction = 4
                NextX=round(LastX+wayPointSread*abs(math.atan((GoToX-LastX)/(GoToY-LastY))))
                NextY=round(LastY-wayPointSread*abs(math.atan((GoToY-LastY)/(GoToX-LastX))))
            #!!!#add a way to tell wich way to project (using absolute angle?)
            
            if i!=0 and direction != lastDirection and lastDirection!=0:
                n+=1
                lastDirection = 0
                if n>=len(self.memory):
                    n=0
            else: 
                lastDirection = direction
            nextWaypoint =(str(NextX)+ ' '+str(NextY))
            waypoints.append(nextWaypoint)
            
        return  (waypoints)
def distanceFormula(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)
# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
memory =[]
laps = int(input())
checkpoint_count = int(input())
for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    memory.append((str(checkpoint_x)+' '+str(checkpoint_y)))
# game loop
FirstPodracer = Podracer()
SecondPodracer = Podracer(FirstPodracer)
FirstPodracer.setAlly(SecondPodracer)
SecondPodracer.setAlly(FirstPodracer)

EnemyA = Podracer()
EnemyB = Podracer()
EnemyA.setAlly(EnemyB)
EnemyB.setAlly(EnemyA)
while True:
    for i in range(2):
        # x: x position of your pod
        # y: y position of your pod
        # vx: x speed of your pod
        # vy: y speed of your pod
        # angle: angle of your pod
        # next_check_point_id: next check point id of your pod
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        NextPointX,NextPointY=memory[next_check_point_id].split(' ')
        NextPointX,NextPointY=int(NextPointX),int(NextPointY)
        
        if i ==0:
            FirstPodracer.setAllValues(x, y, vx, vy, angle, next_check_point_id,NextPointX,NextPointY,memory,EnemyA,EnemyB,SecondPodracer)
        else:
            SecondPodracer.setAllValues(x, y, vx, vy, angle, next_check_point_id,NextPointX,NextPointY,memory,EnemyA,EnemyB,FirstPodracer)
        

    for i in range(2):
        # x_2: x position of the opponent's pod
        # y_2: y position of the opponent's pod
        # vx_2: x speed of the opponent's pod
        # vy_2: y speed of the opponent's pod
        # angle_2: angle of the opponent's pod
        # next_check_point_id_2: next check point id of the opponent's pod
        x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2 = [int(j) for j in input().split()]
        NextPointX,NextPointY=memory[next_check_point_id_2].split(' ')
        NextPointX,NextPointY=int(NextPointX),int(NextPointY)
        
        if i ==0:
            EnemyA.setAllValues(x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2,NextPointX,NextPointY,memory,FirstPodracer,SecondPodracer,EnemyB)
        else:
            EnemyB.setAllValues(x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2,NextPointX,NextPointY,memory,FirstPodracer,SecondPodracer,EnemyA)
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"
    print(FirstPodracer.MainControl())
    print(SecondPodracer.MainControl())