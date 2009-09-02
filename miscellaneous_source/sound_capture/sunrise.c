#include "sound_capture.h"

static int est_sunrise[366] = {287,288,289,289,290,291,292,293,294,295,296,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,316,317,318,320,321,322,323,324,325,326,327,328,329,330,331,331,332,333,334,335,336,337,338,339,340,341,342,343,344,344,345,346,347,348,349,350,351,351,352,353,354,355,356,356,357,358,359,360,360,361,362,363,364,364,365,366,367,367,370,371,371,372,373,374,374,375,376,377,378,378,379,380,381,381,382,383,384,385,385,386,387,388,388,389,390,391,392,393,394,395,396,396,397,398,399,399,400,401,402,402,403,404,405,405,406,407,408,408,409,410,410,411,412,412,413,414,416,416,417,417,418,418,419,419,420,420,421,421,422,422,422,423,423,423,424,424,424,424,424,425,425,425,425,425,425,425,425,425,425,425,424,424,424,424,424,423,423,423,422,422,421,421,420,420,419,419,418,418,417,416,416,415,414,413,413,411,410,409,408,407,406,405,404,403,402,401,400,399,398,397,396,395,394,392,391,390,389,388,386,385,384,382,381,380,379,376,375,373,372,370,369,368,366,365,364,362,361,359,358,356,355,354,352,351,349,348,346,345,344,342,341,339,338,337,335,334,332,331,330,328,327,325,324,323,321,320,319,317,316,315,314,312,311,310,309,307,306,305,304,303,302,301,299,298,297,295,294,293,292,292,291,290,289,288,287,287,286,285,284,284,283,283,282,281,281,280,280,280,279,279,278,278,278,278,277,277,277,277,277,277,277,277,277,277,277,277,278,278,278,278,279,279,279,280,280,281,281,282,282,283,284,284,285,286,286};
static int est_sunset[366] = {1153,1154,1154,1154,1154,1154,1154,1154,1154,1154,1154,1154,1154,1153,1153,1153,1153,1152,1152,1152,1151,1151,1150,1150,1149,1149,1148,1147,1147,1145,1144,1143,1142,1142,1141,1140,1139,1138,1137,1136,1135,1134,1133,1132,1131,1130,1129,1128,1127,1125,1124,1123,1122,1121,1119,1118,1117,1116,1114,1113,1112,1111,1109,1108,1107,1105,1104,1103,1101,1100,1099,1097,1096,1094,1093,1092,1090,1089,1087,1086,1085,1083,1082,1081,1079,1078,1076,1072,1071,1070,1068,1067,1065,1064,1063,1061,1060,1059,1058,1056,1055,1054,1052,1051,1050,1049,1048,1046,1045,1044,1043,1042,1041,1040,1039,1037,1035,1034,1033,1032,1031,1030,1030,1029,1028,1027,1026,1025,1025,1024,1023,1022,1022,1021,1020,1020,1019,1019,1018,1018,1017,1017,1016,1016,1015,1014,1014,1014,1014,1013,1013,1013,1013,1013,1013,1013,1013,1013,1013,1013,1013,1013,1013,1013,1014,1014,1014,1014,1015,1015,1015,1015,1016,1016,1017,1017,1018,1018,1019,1019,1020,1020,1021,1021,1022,1023,1023,1024,1024,1025,1026,1026,1027,1028,1028,1029,1030,1030,1031,1032,1032,1033,1034,1035,1036,1037,1037,1038,1039,1040,1040,1041,1042,1043,1043,1044,1045,1046,1046,1047,1048,1048,1049,1050,1051,1051,1052,1053,1053,1054,1055,1056,1056,1057,1058,1059,1060,1061,1061,1062,1063,1063,1064,1065,1065,1066,1067,1068,1068,1069,1070,1070,1071,1072,1073,1073,1074,1075,1076,1076,1077,1078,1079,1079,1080,1081,1082,1082,1083,1084,1085,1085,1086,1087,1088,1089,1089,1090,1091,1092,1093,1094,1095,1095,1096,1097,1098,1099,1100,1101,1102,1103,1103,1104,1106,1107,1108,1109,1110,1111,1112,1113,1114,1115,1116,1117,1118,1119,1120,1121,1122,1123,1124,1125,1126,1127,1128,1129,1130,1131,1131,1132,1133,1134,1135,1136,1137,1138,1139,1139,1140,1141,1142,1143,1143,1144,1145,1146,1146,1147,1147,1148,1149,1149,1150,1150,1151,1151,1151,1152,1152,1153,1153,1153};

int
calculate_monitoring_priority(time_t t) {
	t += 10*60*60; // eastern standard time offset;
	struct tm *tp = gmtime(&t);
	int sunrise = est_sunrise[tp->tm_yday];
	int sunset = est_sunset[tp->tm_yday];
//	printf("EST sunrise %02d:%02d sunset %02d:%02d\n", sunrise/60, sunrise%60, sunset/60, sunset%60);
	int delta_minutes_sunrise = tp->tm_hour*60 + tp->tm_min - sunrise;
	int delta_minutes_sunset = tp->tm_hour*60 + tp->tm_min - sunset;
	return calculate_monitoring_priority1(delta_minutes_sunrise, delta_minutes_sunset);
}

int
calculate_monitoring_priority1(int delta_minutes_sunrise, int delta_minutes_sunset) {
	if (delta_minutes_sunset > 10 && delta_minutes_sunset < 40) 
		return 9;
	else if (delta_minutes_sunset > -10 && delta_minutes_sunset < 60)
		return 8;
	else if (delta_minutes_sunset > -60 && delta_minutes_sunset < 120)
		return 7;
	else if (delta_minutes_sunrise > -45 && delta_minutes_sunrise < 15)
		return 6;
	else if (delta_minutes_sunrise > -60 && delta_minutes_sunrise < 60)
		return 5;
	else if (delta_minutes_sunrise > 0 && delta_minutes_sunrise < 120)
		return 4;
	else if (delta_minutes_sunset > -120 && delta_minutes_sunset < 0)
		return 4;
	else if (delta_minutes_sunset > 0 && delta_minutes_sunset < 180)
		return 3;
	else if (delta_minutes_sunrise > -120 && delta_minutes_sunrise < 0)
		return 3;
	else if (delta_minutes_sunrise > 0 && delta_minutes_sunset < 0)
		return 2;
	else
		return 1;
}

#ifdef TEST
int main(void) {
	time_t t = time(NULL);
	for (int i = 0; i < 48;i++) {
		printf("Priority %d for %s",  calculate_monitoring_priority(t), ctime(&t));
		t += 0.5*60*60;;
	}
	return 0;
}
#endif
