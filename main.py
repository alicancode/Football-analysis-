from utils import read_video, save_video
from trackers import Tracker
import cv2
from team_assigning import Teamer



def main():
    #extracting video
    video_frames = read_video('08fd33_4.mp4')
    tracker =  Tracker('models_robo/best.pt')
    tracks = tracker.get_object_tracks(video_frames, read_from_stubs = True, stub_pathway = 'stubs/track_stubs.pk1')


#interpolating the ball
    tracks['ball'] = tracker.interpolation(tracks['ball'])

#assiging teams
    team_assigner = Teamer()
    team_assigner.assign(video_frames[0], tracks['players'][0])

    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num],
                                                 track['bbox'],
                                                 player_id)
            
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]

    #draw object
    output_video_frames = tracker.draw_annotations(video_frames, tracks)
    #save video

    save_video(output_video_frames, 'output_videos/output2.avi')

if __name__ == '__main__':
    main()