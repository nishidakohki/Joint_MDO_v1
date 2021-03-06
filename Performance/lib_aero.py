
# LAP TIME
from __future__ import division

from scipy.optimize import *
import numpy as np
import matplotlib.pyplot as plt

from AVL.avl_lib import *
from xfoil.xfoil_lib import *

from runwaysim.lib_runwaysim_small import runway_sim_small

# Declare Consonstants

Rho = 1.225 # make global
# Sref_tail = 0.212
g = 9.81
mu_k = 0.005

inced_ang = -5.0 *np.pi/180.0

xfoil_path = '/home/josh/Documents/Research/MACHMDO/runwaysim/xfoil/elev_data'


alphas_tail, CLs_tail_flap = getData_xfoil(xfoil_path+ '_flap.dat')[0:2]
alphas_tail_noflap,CLs_tail_noflap = getData_xfoil(xfoil_path+ '.dat')[0:2]
alphas_tail = [x * np.pi/180 for x in alphas_tail]
CL_tail_flap = np.poly1d(np.polyfit(alphas_tail,CLs_tail_flap, 2))
CL_tail_noflap = np.poly1d(np.polyfit(alphas_tail_noflap,CLs_tail_noflap, 2))



def thrust(vel, ang):
	T_0 = 18.00
	T_1 = -0.060
	T_2 = -0.015
	T_3 = 0 #-7*10**-5*3.28**3
	T_4 = 0 # 4*10**-7*3.28**4

	T = vel**4*T_4 + vel**3*T_3 + vel**2*T_2 + vel*T_1 + T_0
			#X comp   # Y Comp
	return (np.cos(ang)*T, np.sin(ang)*T )

def tail_CL(ang, flapped):
	if (flapped):
		return CL_tail_flap(ang + inced_ang)
	else:
		return CL_tail_noflap(ang + inced_ang)

def gross_lift(vel, ang, Sref_wing, Sref_tail, flapped, CL):
	l_net = 0.5*Rho*vel**2*(CL(ang)*Sref_wing + tail_CL(ang, flapped)*Sref_tail)

	gross_F = l_net + thrust(vel,ang)[1]

	return gross_F




def calc_velcruise(CL, CD, weight, Sref_wing, Sref_tail):	
	def sum_forces (A):
		vel = A[0]
		ang = A[1]


		F = np.empty(2)

		F[0] = thrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*Sref_wing
		F[1] = gross_lift(vel, ang, Sref_wing, Sref_tail, 0, CL) - weight
		# print(F)
		return F

 	Z = fsolve(sum_forces,np.array([40, -10*np.pi/180]))

 	ang = Z[1]
 	vel =  Z[0]

 	return (vel, ang)

def calc_climb(CL, CD, weight, Sref_wing, Sref_tail):

	
	def sum_forces (A ):

		vel = A[0]
		gamma = A[1]
		# print("vel: " + str(vel))
		# print("gamma: " + str(gamma))

		F = np.empty(2)

		F[0] = thrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*Sref_wing - weight*np.sin(gamma)
		F[1] = gross_lift(vel, ang, Sref_wing,Sref_tail, 0, CL) - weight*np.cos(gamma)
		# print(F)
		return F

	sol = np.empty((0,3), float)
	A = np.zeros((1,3))
	AoA = []

	for ang in np.linspace(0*np.pi/180, 5*np.pi/180, 30):

		AoA.append(ang)
		# print(ang)
		Z = fsolve(sum_forces,np.array([15.0, 0*np.pi/180]),)

		A[0,0] = Z[0]
		A[0,1] = Z[1]
		A[0,2] = np.sin(Z[1])*Z[0]

		sol = np.append(sol, A, axis=0)

	V_climb = np.max(sol[:,2])

	index = np.where(sol[:,2] == V_climb)[0][0]

	AoA_climb = AoA[index]
	vel_climb = sol[index,0]

	# fig, ax1 = plt.subplots()
	# ax1.plot(AoA, sol[:,1], 'b-')
	# ax1.set_xlabel('time (s)')
	# # Make the y-axis label and tick labels match the line color.
	# ax1.set_ylabel('gamma', color='b')
	# for tl in ax1.get_yticklabels():
	#     tl.set_color('b')

	# ax2 = ax1.twinx()
	# ax2.plot(AoA, sol[:,2] , 'r-')
	# ax2.set_ylabel('V_climb', color='r')
	# for tl in ax2.get_yticklabels():
	#     tl.set_color('r')

	# plt.show()

	horz_Vel = np.cos(sol[index,1])*vel_climb
	# print(horz_Vel)

	return(vel_climb, V_climb, horz_Vel, AoA_climb)

def cruise(dist, velocity):
	time = dist/velocity
	return time 

def turn(bank_angle, velocity, weight ,Sref_wing, turn_angle):
	velocity = velocity/2

	bank_angle_r = bank_angle*np.pi/180
	g = 9.81

	rad = velocity**2/(np.tan(bank_angle)*g)
	CL = (weight*2)/(np.cos(bank_angle_r)*Sref_wing*Rho*velocity**2)

	time = (rad*2*np.pi*(turn_angle/360))/velocity

	return time



def runway_sim_small(CL, CD, CM, Sref_wing, Sref_tail, weight, boom_len, dist_LG, MAC, Iyy):

	Flapped = 0
	max_rot_ang = 10*np.pi/180.0


	#declare functions for kinimatic varibles (F = ma and M = I*ang_a)

	# super trivail func, but it helped me organize my thoughts
	def velocity(vel):
		return vel

	def acceleration(vel, ang):
		N =  weight - gross_lift(vel,ang, Sref_wing, Sref_tail, Flapped,CL)
		if N < 0:
			N = 0
		accel = (g/weight)*(thrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*Sref_wing - mu_k*N)
		return accel

	def ang_velocity(a_vel, ang):
		if (ang <= 0.0 and a_vel < 0.0) :
			a = 0
		elif (ang >= max_rot_ang and a_vel > 0.0):
			a = 0
		else:
			a = a_vel


		return a

	def ang_acceleration(vel, ang, v_ang):
		q = 0.5*Rho*vel**2
		moment_tail = - q*tail_CL(ang, Flapped)*Sref_tail*(boom_len - dist_LG)
		moment_wing = q*(CM(ang)*Sref_wing*MAC+ CL(ang)*Sref_wing*dist_LG)
		# damping_moment =  -np.sign(a_vel)*0.5*Rho*a_vel**2*50*Sref_wing
		ang_accel = 1.0/(Iyy + (weight/g)*dist_LG**2)*(moment_wing+moment_tail) # +damping_moment)
		
		if (ang <= 0.0 and ang_accel < 0.0) :
			ang_accel = 0
		elif (ang >= max_rot_ang and v_ang >= 0.0):
			ang_accel = -30*v_ang
			if (abs(ang_accel) < 10**-27 and Flapped):
				ang_accel = 0

		else:

			pass

		return ang_accel

	# main loop
	i = 0

	dist = [0.0]
	vel = [0.0]
	ang = [0.0]
	ang_vel = [0.0]

	# accel = [acceleration(vel[i], ang[i ])]
	# ang_accel = [ ang_acceleration(vel[i], ang[i], ang_vel[i]) ]


	v_stall = np.sqrt(2*weight/(Rho*Sref_wing*1.7))


	time = [0.0]
	dt = 0.2
	time_elap = 0

	# DT =[dt]

	sum_y =  gross_lift(vel[i],ang[i], Sref_wing, Sref_tail, Flapped, CL) - weight

	while (sum_y <= 0.0 and time_elap < 20) :

		# F = ma yeilds two second order equations => system of 4 first order
		# runge Kutta 4th to approximate kinimatic varibles at time = time + dt
		k1_dist = dt*velocity(vel[i])
		k1_vel = dt*acceleration(vel[i],ang[i])
		k1_ang = dt*ang_velocity(ang_vel[i], ang[i])
		k1_ang_vel = dt*ang_acceleration(vel[i], ang[i], ang_vel[i])

		k2_dist = dt*velocity(vel[i] + 0.5*k1_vel)
		k2_vel = dt*acceleration(vel[i] + 0.5*k1_vel, ang[i] + 0.5*k1_ang)
		k2_ang = dt*ang_velocity(ang_vel[i] + 0.5*k1_ang, ang[i] + 0.5*k1_ang)
		k2_ang_vel = dt*ang_acceleration(vel[i] + 0.5*k1_vel, ang[i] + 0.5*k1_ang, ang_vel[i] + 0.5*k1_ang_vel)

		k3_dist = dt*velocity(vel[i] + 0.5*k2_vel)
		k3_vel = dt*acceleration(vel[i] + 0.5*k2_vel, ang[i] + 0.5*k2_ang)
		k3_ang = dt*ang_velocity(ang_vel[i] + 0.5*k2_ang, ang[i] + 0.5*k2_ang)
		k3_ang_vel = dt*ang_acceleration(vel[i] + 0.5*k2_vel, ang[i] + 0.5*k2_ang, ang_vel[i] + 0.5*k2_ang_vel)

		k4_dist = dt*velocity(vel[i] +  k3_vel)
		k4_vel = dt*acceleration(vel[i] + k3_vel, ang[i] + k3_ang)
		k4_ang = dt*ang_velocity(ang_vel[i] + k3_ang, ang[i] + k3_ang)
		k4_ang_vel = dt*ang_acceleration(vel[i] + k3_vel, ang[i] + k3_ang, ang_vel[i] + k3_ang_vel)

		dist.append(dist[i] + 1.0/6*(k1_dist + 2*k2_dist + 2*k3_dist + k4_dist))
		vel.append(vel[i] + 1.0/6*(k1_vel + 2*k2_vel + 2*k3_vel + k4_vel))
		ang.append(ang[i] + 1.0/6*(k1_ang + 2*k2_ang + 2*k3_ang + k4_ang)) 
		ang_vel.append(ang_vel[i] + 1.0/6*(k1_ang_vel + 2*k2_ang_vel + 2*k3_ang_vel + k4_ang_vel))
		# accel.append(acceleration(vel[i + 1], ang[i + 1]))
		# ang_accel.append(ang_acceleration(vel[i + 1], ang[i+ 1], ang_vel[i+1]))


		i = i + 1

		if abs(ang_vel[i])< 10**-8 and Flapped:
			ang_vel[i] = 0.0

		if ang[i] > max_rot_ang:
			ang[i] = max_rot_ang
		elif ang[i] < 0.0:
			ang[i] = 0.0


		if (vel[i] < 0.92*(v_stall+2.0)) or (abs(ang_vel[i]) == 0.0 and (ang[i] < 10**-10 or ang[i] >=max_rot_ang)) :
			dt = 0.2
		else:
			dt = 0.05
		# DT.append(dt)
		
		time.append(time[i -1] + dt)
		time_elap = time[i]

		sum_y =  gross_lift(vel[i],ang[i], Sref_wing,Sref_tail, Flapped, CL) - weight


		if vel[i] > v_stall+2.0:
			Flapped = 1
		


	# runway_len = 200 #meters

	if (sum_y > 0.0 and dist[i] <= 200.0):
		takeoff = 1
	else:
		takeoff = 0

	# ============== Ploting ===============

	# plt.figure(1)
	# plt.subplot(711)
	# plt.ylabel('Angle)')
	# plt.xlabel('time')
	# plt.plot(time, ang, 'b')

	# plt.subplot(712)
	# plt.ylabel('ang velocity')
	# plt.xlabel('time')
	# plt.plot(time, ang_vel, 'b')

	# # plt.subplot(713)
	# # plt.ylabel('ang acceleration')
	# # plt.xlabel('time')
	# # plt.plot(time, ang_accel, 'b')

	# plt.subplot(714)
	# plt.ylabel('distance')
	# plt.xlabel('time')
	# plt.plot(time, dist, 'b')

	# plt.subplot(715)
	# plt.ylabel('Velocity')
	# plt.xlabel('time')
	# plt.plot(time, vel, 'b')

	# # plt.subplot(716)
	# # plt.ylabel('Acceleration')
	# # plt.xlabel('time')
	# # plt.plot(time, accel, 'b')

	# # plt.subplot(717)
	# # plt.ylabel('dt')
	# # plt.xlabel('time')
	# # plt.plot(time, DT, 'b')
	# plt.show()

	
	# print('Takeoff:' + str(takeoff))
	# print('Distance: ' + str(dist[i]))
	# print('vel: ' + str(vel[i]))
	# print('ang: ' + str(ang[i]*180.0/np.pi) + ' max_rot_ang: ' + str(max_rot_ang*180.0/np.pi))
	# print('ang_vel: ' + str(ang_vel[i]))
	# print('time: ' + str(time[i]))
	# print('steps: ' + str(len(time)))
	# print('\n')

	return (takeoff, dist[i], vel[i], ang[i], ang_vel[i], time[i])

def num_laps(CL, CD, CM, Sref_wing, Sref_tail, weight, boom_len, dist_LG, MAC, Iyy):

	max_time = 4*60.0
	N = 0

	leg_len = 500*0.3048
	Flapped = 0

	cruise_vel, cruise_Ang = calc_velcruise(CL, CD, weight, Sref_wing, Sref_tail)
	climb_vel, climb_hvel = calc_climb(CL, CD, weight, Sref_wing, Sref_tail)[1:3]

	
	# if climb_vel <= 0.5 or cruise_vel <= 6.0:
	# 	print('Can not Climb/Cruise is slow' + ' V_climb: ' + str(climb_vel) + ' Vel_Cruise: ' + str(cruise_vel))
	# 	return 0, 0.0

	if climb_vel <= 0.5 or cruise_vel < 7.0 :
		print('Can not Climb' + ' V_climb: ' + str(climb_vel) + '  cruise_vel=' + str(cruise_vel))
		return 0, 0.0

	# print('cruise_vel =' + str(cruise_vel)+  ' cruise_Ang: ' + str(cruise_Ang) + 'climb_vel = ' + str(climb_vel) + ' climb_hvel =' + str(climb_hvel))

	# ==========================  beign takeoff ===========================
	#find time to takeoff
	takeoff,dist, vel, ang, ang_vel, time =  runway_sim_small(CL, CD, CM, Sref_wing, Sref_tail, weight, boom_len, dist_LG, MAC, Iyy)
	


	if takeoff == 0:
		print('Failed to Takeoff')
		return 0, 999


	alt_cruise = 15.5



	time_to_alt = alt_cruise/climb_vel

	time = time + time_to_alt
	dist = dist + climb_hvel*time_to_alt

	if dist < leg_len:
		time = time + cruise(leg_len - dist, cruise_vel)

	time = time + turn(35, cruise_vel, Sref_wing, weight, 180)
	time = time + cruise(leg_len, cruise_vel)
	time = time + turn(40, cruise_vel, Sref_wing, weight, 360)
	time = time + cruise(leg_len, cruise_vel)
	time = time + turn(35, cruise_vel, Sref_wing, weight, 180)
	time = time + cruise(leg_len, cruise_vel)

	while time < max_time:
		N = N + 1

		time = time + cruise(leg_len , cruise_vel)
		time = time + turn(35, cruise_vel, Sref_wing, weight, 180)
		time = time + cruise(leg_len, cruise_vel)
		time = time + turn(40, cruise_vel, Sref_wing, weight, 360)
		time = time + cruise(leg_len, cruise_vel)
		time = time + turn(35, cruise_vel, Sref_wing, weight, 180)
		time = time + cruise(leg_len, cruise_vel)
	
		# print(N)
	return (N,time)


