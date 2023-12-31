from typing import Any
import numpy as np
import gymnasium as gym
from gymnasium import spaces

#blackJack
class BlackJackEnv(gym.Env):
    def __init__(self):
        super(BlackJackEnv, self).__init__()

        self.action_space = spaces.Discrete(3)
        # 0 for stay,1 for hit,2 for split
        self.observation_space = self.observation_space = spaces.Dict({"player_sum": spaces.Discrete(32),"player_sum2": spaces.Discrete(32), "dealer_sum": spaces.Discrete(32),"usable_ace":spaces.Discrete(2),"usable_ace2":spaces.Discrete(2),"split_avalibale": spaces.Discrete(2),"current_hand":spaces.Discrete(2) }, seed=42)
        
        self.reset()
        
    def reset(self,seed=None, options=None):
            # Initialize the state
            self.player_sum = 0
            self.dealer_sum = 0
            self.player_usable_ace = 0
            self.player_ace_count=0
            self.dealer_usable_ace = False
            self.dealer_ace_count=0
            self.done = False
            self.last_hand=True #for splitting 
            #for making the split
            self.hand2_sum = 0
            self.hand2_usable_ace =0
            self.hand2_ace_count =0
            self.hand1_not_scored= True
            self.current_hand= 1

            # Deal initial cards
            mode= np.random.choice(['1','2'])
            if mode =='1':
               self.player_sum,self.player_ace_count, self.player_usable_ace,card1 =self._deal_card(self.player_sum,self.player_ace_count, self.player_usable_ace)
               
               self.player_sum,self.player_ace_count, self.player_usable_ace,card2=self._deal_card(self.player_sum,self.player_ace_count, self.player_usable_ace)
               
            else:
                 self.player_sum,self.player_ace_count, self.player_usable_ace,card1,card2=self.make_double(self.player_sum,self.player_ace_count, self.player_usable_ace)
          
            
            
            self.dealer_sum, self.dealer_ace_count,self.dealer_usable_ace,demi =self._deal_card(self.dealer_sum,self.dealer_ace_count,self.dealer_usable_ace)
            # Flag for checking if split is available
            self.split_available = int(card2 == card1)
                 

            return self._get_obs(),{}   
    def make_double(self,sum,ace_count,usable_ace):
         card = np.random.choice(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K','A'])
         card2=card
         cards_value= {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,"Q":10,"K":10,"A":11}
         sum += cards_value[card]
          # Check for a usable ace
         if card == 'A':
               ace_count +=1
               
               usable_ace=True
               
        

        # If the sum is over 21 and there is a usable ace, convert it to a 1
         if sum > 21 and usable_ace:
            sum -= 10
            ace_count-=1
            if ace_count>=1:
                 usable_ace=True
            else: usable_ace=False
          
         return sum, ace_count, usable_ace, card, card2
     

    def _deal_card(self,sum,ace_count,usable_ace):
          # Deal a card to the player or dealer
        card = np.random.choice(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K','A'])
        #card=input('coose card')
        cards_value= {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,"Q":10,"K":10,"A":11}
       
        sum += cards_value[card]
          # Check for a usable ace
        if card == 'A':
             ace_count +=1
             
             usable_ace=True
            
        

        # If the sum is over 21 and there is a usable ace, convert it to a 1
        if sum > 21 and usable_ace:
            sum -= 10
            ace_count-=1
            if ace_count>=1:
                 usable_ace=True
            else: usable_ace=False
        
        
        

        return sum, ace_count, usable_ace, card

    def _get_obs(self):
        # Return the current state as an observation 
        
        obs={"player_sum" :self.player_sum,"player_sum2":self.hand2_sum, "dealer_sum" :self.dealer_sum,"usable_ace" :self.player_usable_ace,"usable_ace2" :self.hand2_usable_ace,"split_avalibale" :self.split_available,"current_hand":self.current_hand}
        return obs

    def step(self,action):
        reward=0
        if action == 1: #hit
              
              
              if self.hand2_sum ==0:#only one hand
                  self.player_sum,self.player_ace_count, self.player_usable_ace,demi =self._deal_card(self.player_sum,self.player_ace_count, self.player_usable_ace)
                  if self.player_sum >21:
                     
                        reward -= 1
                        self.done = True
              else:    #two hands cade
                   if self.last_hand == False: #first of two hands
                        self.player_sum,self.player_ace_count, self.player_usable_ace,demi =self._deal_card(self.player_sum,self.player_ace_count, self.player_usable_ace)
                        if self.player_sum >21:
                            self.current_hand=2
                            self.hand1_not_scored= False
                            self.last_hand=True
                            reward -= 1
                        
                   else:  #the second hand is playing
                             self.hand2_sum,self.hand2_ace_count, self.hand2_usable_ace,demi =self._deal_card(self.hand2_sum,self.hand2_ace_count, self.hand2_usable_ace)
                             if self.hand2_sum >21:
                                  reward -= 1
                                  if self.hand1_not_scored == True:
                                        while self.dealer_sum < 17:
                                             self.dealer_sum, self.dealer_ace_count,self.dealer_usable_ace,demi = self._deal_card(self.dealer_sum,self.dealer_ace_count, self.dealer_usable_ace)
                                        
                                        if self.dealer_sum >21 or self.hand2_sum > self.dealer_sum:
                                             reward +=1
                                        elif self.dealer_sum>self.hand2_sum:
                                             reward-=1

                              
                                        self.done = True
                        
                   
            
        if action == 0: #stand
             
             if self.hand2_sum ==0:#one hand case
                while self.dealer_sum < 17:
                        self.dealer_sum, self.dealer_ace_count,self.dealer_usable_ace,demi = self._deal_card(self.dealer_sum,self.dealer_ace_count, self.dealer_usable_ace)
                if self.dealer_sum >21 or self.player_sum > self.dealer_sum:
                     reward +=1
                
                elif self.dealer_sum > self.player_sum:
                     reward -=1
                

                self.done =True
            
             elif self.hand2_sum !=0 and self.last_hand==False: #first hand finished second didnt
                  self.last_hand=True
                  self.current_hand=2
            
             else: #both hands finished
                  while self.dealer_sum < 17:
                        self.dealer_sum, self.dealer_ace_count,self.dealer_usable_ace,demi = self._deal_card(self.dealer_sum,self.dealer_ace_count, self.dealer_usable_ace)
                  if self.dealer_sum >21 or self.player_sum > self.dealer_sum:
                     reward +=1
                
                  elif self.dealer_sum > self.player_sum:
                     reward -=1
                  if self.dealer_sum >21 or self.hand2_sum > self.dealer_sum:
                     reward +=1*self.hand1_not_scored
                  elif self.dealer_sum>self.hand2_sum:
                      reward-=1*self.hand1_not_scored
                  self.done =True
                
                   
             
                
            
                  
                

                
        if action ==2 : #splitting
            
            if self.split_available == False:
                  reward -=10
                  self.done =True
                  
            
            else: 
                    self.last_hand = False
                    self.split_available =False
                    if self.player_usable_ace == True:
                         self.player_sum,self.hand2_sum = 11,11
                         self.player_ace_count,self.hand2_ace_count = 1,1
                         self.player_usable_ace, self.hand2_usable_ace =True,True
                    else:
                         self.player_sum, self.hand2_sum =self.player_sum/2,self.player_sum/2


                
        return self._get_obs(), reward, self.done,False, {}              
                 
            
    
    
    
             

    def render(self):
        pass

    def set_stage(self,sum1,dealersum,ace,split):
     self.player_sum =sum1
     self.dealer_sum=dealersum
     self.usable_ace=ace
     self.split_available=split
     return None
   



#cheking

#i=True             
#while i==True:
  #   j=int(input('make_move'))
           
   #  q,w,r,g,b=env.step(action=j)
   #  print(q,w)
   #  if r==True:
         
    #   break

