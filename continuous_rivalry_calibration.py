from psychopy import visual, core, event, monitors
import numpy as np

# =========================
# NEED TO DO
# =========================
# right now it exits if you press no buttons or wrong buttons as if the eyes were perfectly balanced 
# it's taking .01 off the top of one of the contrasts after it has already converged
# currently shows you all your timing stuff in between trials just for testing purposes, prolly want to eventually get rid of that

# =========================
# PARAMETERS
# =========================
contrast_L = 1.0
contrast_R = 1.0

max_trials = 8
trial_duration = 60
rest_duration = 5 # not relevant right now

clock = core.Clock()
distance_from_center = 600
stim_size = 200
border_size = 150
fixation_size = 200
scale_everything = 0.66


win = visual.Window(units="pix", 
                    fullscr=True, 
                    screen=0, 
                    color=(-1.0, -1.0, -1.0)) # black background



# =========================
# INFO SELECTED AT START
# =========================
#pp_nr = 'test'
#
#myDlg = gui.Dlg(title="Calibration parameters")
#myDlg.addField('Subject nr:', pp_nr, required=True)
#

# =========================
# LOAD STIMULI
# =========================
img_L = visual.ImageStim(
    win,
    image='./images/grating_vertical_green.png',
    pos=((-1.0 * distance_from_center), 0),
    size=stim_size * scale_everything
)

img_R = visual.ImageStim(
    win,
    image='./images/grating_horizontal_magenta.png',
    pos=(distance_from_center, 0),
    size=stim_size*scale_everything
)

# shared frame image
frame_L = visual.ImageStim(
    win,
    image='./images/frame_transparent-border.png',
    pos=((-1.0 * distance_from_center), 0),
    size=border_size*scale_everything
)

frame_R = visual.ImageStim(
    win,
    image='./images/frame_transparent-border.png',
    pos=(distance_from_center, 0),
    size=border_size*scale_everything
)

fix_L = visual.ImageStim(
    win, 
    image='./images/fixation_cross.png', 
    pos=((-1.0 * distance_from_center), 0), 
    size=fixation_size*scale_everything)
    
fix_R = visual.ImageStim(
    win, 
    image='./images/fixation_cross.png', 
    pos=(distance_from_center, 0), 
    size=fixation_size*scale_everything)

#fixation = visual.TextStim(win, text='+', height=0.5)


# =========================
# CALIBRATION LOOP
# =========================
for trial in range(max_trials):

    print(f"\nTrial {trial+1}")
    print(f"Contrast L: {contrast_L:.3f}, R: {contrast_R:.3f}")

    left_time = 0
    right_time = 0
    mixed_time = 0

    last_key = None
    last_time = 0

    clock.reset()
    event.clearEvents()

    # =========================
    # RIVALRY LOOP
    # =========================
    while clock.getTime() < trial_duration:

        t = clock.getTime()
        dt = t - last_time

        # ignore first 2 seconds
        if t > 2:
            if last_key == 'j':
                left_time += dt
            elif last_key == 'l':
                right_time += dt
            elif last_key == 'k':
                mixed_time += dt

        keys = event.getKeys(keyList=['j', 'k', 'l', 'escape'])

        if 'escape' in keys:
            win.close()
            core.quit()

        if len(keys) > 0:
            last_key = keys[-1]

        last_time = t

        # apply contrast
        img_L.opacity = contrast_L
        img_R.opactiy = contrast_R

        # draw
        img_L.draw()
        img_R.draw()
        frame_L.draw()
        frame_R.draw()
        fix_L.draw()
        fix_R.draw()

        win.flip()
    
    
    # =========================
    # COMPUTE DOMINANCE
    # =========================
    total = left_time + right_time # NOTE: i saw a paper doing this way, alternatively we could do total time including mix percepts as well?? 
    total_with_mix = left_time + right_time + mixed_time

    if total == 0:
        print("No valid dominance reported → skipping update")
        continue  # <-- better than forcing 0.5

    left_prop = left_time / total 
    right_prop = right_time / total
    mix_prop = mixed_time / total_with_mix 

    diff = right_prop - left_prop
    abs_diff = abs(diff)

    print(f"total time without mix: {total:.3f}")
    print(f"total time WITH mix: {total_with_mix:.3f}")
    print(f"Left time: {left_time:.3f}, Right time: {right_time:.3f}, Mix time: {mixed_time:.3f}")
    print(f"Left prop: {left_prop:.3f}, Right prop: {right_prop:.3f}, Mix prop: {right_prop:.3f}")

    # =========================
    # REST BETWEEN TRIALS 
    # =========================
    frame_L.draw()
    frame_R.draw()
    fix_L.draw()
    fix_R.draw()
    win.flip()
#    core.wait(rest_duration)
    
    update_text = f"total time without mix: {total:.3f} \ntotal time WITH mix: {total_with_mix:.3f} \nLeft time: {left_time:.3f} \nRight time: {right_time:.3f} \nMix time: {mixed_time:.3f} \nLeft prop: {left_prop:.3f} \nRight prop: {right_prop:.3f} \nMix prop: {right_prop:.3f} \nPress space to continue. \nRight - Left = {diff:.3f}"
    summary_text = visual.TextStim(win, text=update_text) # height=1)
    summary_text.draw()
    win.flip()
    #event.waitKeys()
    event.waitKeys(keyList=['space'])
    
    # =========================
    # STEP SIZE
    # =========================
    if abs_diff >= 0.20:
        step_size = 0.10
    elif abs_diff > 0.05:
        step_size = 0.05
    else:
        step_size = 0.01

    print(f"Step size: {step_size:.3f}")

    # =========================
    # ADJUST DOMINANT EYE
    # =========================
    if abs_diff > 0.02:
        if diff > 0:
            contrast_R -= step_size
        else:
            contrast_L -= step_size

    contrast_L = np.clip(contrast_L, 0.1, 1.0)
    contrast_R = np.clip(contrast_R, 0.1, 1.0)

    # =========================
    # STOPPING RULE
    # =========================
    if abs_diff <= 0.05 and trial >= 1: # make sure they do 2 trials at very least no matter what 
        print("Converged.")
        break

# =========================
# FINAL SCREEN
# =========================
print("\nFinal contrasts:")
print(f"Left: {contrast_L:.3f}")
print(f"Right: {contrast_R:.3f}")

final_text = visual.TextStim(win, text=f"Calibration done \nFinal contrasts: \nLeft: {contrast_L:.3f} \nRight: {contrast_R:.3f} \nPress SPACE to end", height=0.5)
final_text.draw()
win.flip()
#event.waitKeys()
event.waitKeys(keyList=['space'])

win.close()
core.quit()