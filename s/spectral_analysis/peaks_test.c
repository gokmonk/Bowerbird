#include "i.h"
//iota 1 1000|randomize_lines|tr '\n' ','

int
find_peaks_simple(int length, double * restrict data, int * restrict peaks) {
	int n_peaks = 0;
	int radius = param_get_integer("spectral_analysis", "peak_radius");
	double min_height = param_get_double("spectral_analysis", "peak_min_height");
	for (int i = radius; i < length-radius; i++) {
		if (data[i] <= min_height)
			continue;
		int j;
		for (j = i - radius; j <= i+radius; j++)
			if (j != i && data[j] >= data[i])
				break;
		if (j > i+radius) {
			peaks[n_peaks++] = i;
			dp(27, "peak at %d\n", i);
		}
	}
	return n_peaks;
}


static void test_peaks(int n, double data[]) {
	int peaks[n];
	int correct_peaks[n];
	int n_correct_peaks = find_peaks_simple(n, data, correct_peaks);
	for (int i = 0; i < n_correct_peaks; i++)
		dp(21, "%d(%g),", correct_peaks[i],data[correct_peaks[i]]);
	dp(21, "\n");
	int n_peaks = find_peaks_simple(n, data, peaks);
	for (int i = 0; i < n_peaks; i++)
		dp(21, "%d(%g),", peaks[i],data[peaks[i]]);
	dp(21, "\n");
	assert(n_correct_peaks == n_peaks);
	for (int i = 0; i < n_correct_peaks; i++)
		assert(correct_peaks[i] == peaks[i]);
}

static void test_peaks0(void) {
	param_set_integer("spectral_analysis", "peak_radius", 3);
	double data[] = {0,1,2,3,4,3,2,1,2,3,2,13,1,0,1,2,3,4,3,2,1,2,3,2,13};
//	int correct_peaks[] = {4,11,17};
	test_peaks(sizeof data/sizeof data[0], data);
}

static void test_peaks1(void) {
	param_set_integer("spectral_analysis", "peak_radius", 5);
	double data[] = {272,341,635,120,879,747,916,940,141,874,360,657,905,953,877,118,805,612,165,760,824,557,197,338,992,749,625,304,399,601,431,288,477,773,525,88,346,319,162,701,412,588,841,483,528,280,764,765};
//	int correct_peaks[] = {7,13,24,33,42};
	test_peaks(sizeof data/sizeof data[0], data);
}

static void test_peaks2(void) {
	param_set_integer("spectral_analysis", "peak_radius", 13);
	double data[] = {169,161,754,126,434,9,646,421,494,248,69,798,995,539,815,994,57,395,96,843,741,436,502,63,653,968,708,644,866,446,757,907,642,982,93,624,546,570,943,377,549,904,14,86,594,956,225,571,418,321,562,929,985,342,902,937,212,420,131,316,538,781,142,989,154,8,44,755,106,605,231,369,724,738,650,660,484,693,923,186,578,666,480,975,522,856,223,198,981,573,915,913,220,763,388,614,94,691,858,520,782,191,690,34,307,260,54,359,66,616,560,157,507,48,127,310,209,27,166,43,772,547,743,82,11,493,819,535,433,487,200,842,728,792,328,774,216,725,192,999,274,270,998,682,804,959,979,24,5,604,71,756,351,722,758,16,397,702,401,255,634,990,643,500,626,572,419,512,448,357,180,855,350,697,759,275,117,294,470,576,402,302,440,829,375,891,331,704,58,104,599,852,356,960,201,526,935,687,768,361,102,534,55,680,368,478,734,145,732,961,622,918,42,184,362,177,920,619,403,740,597,36,577,155,415,750,835,227,633,951,864,510,51,482,376,524,847,210,645,124,593,240,345,681,222,797,235,1000,167,408,23,315,846,19,463,456,542,540,73,551,77,530,870,143,246,17,336,31,189,56,684,499,380,107,794,839,731,466,385,707,719,95,583,917,946,504,97,621,374,84,696,311,425,984,536,485,737,689,717,579,251,947,922,363,37,320,132,465,529,330,130,404,115,950,204,133,98,544,674,786,265,153,386,575,224,347,868,949,211,81,323,909,679,838,29,896,442,652,574,45,770,490,518,590,899,221,814,92,26,667,78,327,276,532,585,873,394,567,793,406,324,460,365,668,414,384,568,168,486,531,802,706,513,889,678,287,978,91,411,213,196,720,955,675,41,821,139,787,559,910,515,389,558,569,202,181,890,887,685,822,244,136,432,99,76,423,767,469,439,269,970,400,677,860,514,65,880,527,339,150,683,882,22,742,789,775,15,429,489,705,449,371,591,832,241,293,861,658,462,893,630,67,581,620,700,508,101,303,595,256,761,744,958,936,52,867,381,313,32,215,670,649,503,417,898,921,90,219,769,830,344,135,872,833,113,878,18,556,353,641,582,13,122,516,297,801,295,663,278,182,451,263,268,176,355,206,291,941,766,973,289,453,473,205,317,149,305,665,901,298,552,252,826,664,444,450,800,545,258,971,128,598,12,869,629,391,977,299,807,112,596,987,147,195,888,286,441,218,370,783,825,892,903,152,972,452,103,771,736,314,28,631,712,409,378,259,753,817,125,809,62,352,784,925,383,367,615,33,623,89,714,479,863,416,517,711,335,762,808,791,939,883,919,151,475,426,931,561,343,38,884,261,207,613,726,245,238,699,312,924,438,83,445,284,933,410,296,348,47,897,900,422,437,563,2,974,208,976,565,501,35,158,4,405,30,554,876,862,498,659,584,300,178,957,121,859,488,146,188,183,6,100,541,948,264,217,457,459,820,803,836,676,46,53,430,550,308,602,718,229,354,170,628,587,796,390,954,617,174,175,636,496,249,564,906,647,952,669,745,64,237,199,129,600,464,392,491,610,686,435,108,393,105,823,908,655,137,138,427,326,983,849,187,318,811,656,627,476,20,944,776,748,648,428,109,159,964,709,519,114,285,927,962,914,980,358,266,1,844,495,337,848,309,969,729,80,85,306,965,993,50,226,834,322,537,349,228,247,850,752,39,715,505,233,301,443,214,996,424,21,387,566,366,379,589,468,283,895,911,580,548,160,816,242,481,966,292,279,609,373,733,521,282,458,840,329,325,875,886,618,472,334,632,606,851,799,461,942,818,257,845,853,398,912,123,777,986,894,662,185,751,586,271,7,471,735,236,250,111,3,243,739,671,70,509,232,253,110,194,934,603,281,262,190,881,555,640,608,179,932,234,87,75,364,267,10,59,290,806,254,447,991,716,171,116,926,795,239,827,413,455,407,60,277,703,746,119,945,40,780,785,492,651,713,723,25,813,592,173,332,164,533,779,506,61,692,788,140,553,230,871,997,156,639,372,857,885,694,382,454,988,727,474,938,963,203,193,930,543,810,74,831,134,333,144,698,148,837,467,967,828,607,340,688,673,611,273,812,637,695,49,661,854,511,79,730,672,790,172,163,638,72,68,778,523,654,497,396,928,721,710,865,272,341,635,120,879,747,916,940,141,874,360,657,905,953,877,118,805,612,165,760,824,557,197,338,992,749,625,304,399,601,431,288,477,773,525,88,346,319,162,701,412,588,841,483,528,280,764,765};
//	int correct_peaks[] = {33,63,88,139,161,193,209,229,247,262,293,313,327,376,410,452,499,531,563,580,617,633,666,700,724,739,757,775,806,829,851,867,891,919,976};
	test_peaks(sizeof data/sizeof data[0], data);
}

static void test_peaks3(void) {
	param_set_integer("spectral_analysis", "peak_radius", 1);
	double data[] = {272,341,635,120,879,747,916,940,141,874,360,657,905,953,877,118,805,612,165,760,824,557,197,338,992,749,625,304,399,601,431,288,477,773,525,88,346,319,162,701,412,588,841,483,528,280,764,765};
	test_peaks(sizeof data/sizeof data[0], data);
}

int 
main(int argc, char*argv[]) {
	testing_initialize(&argc, &argv, "");
	g_test_add_func("/spectral_analysis/peaks peaks", test_peaks0);
	g_test_add_func("/spectral_analysis/peaks peaks", test_peaks1);
	g_test_add_func("/spectral_analysis/peaks peaks", test_peaks2);
	g_test_add_func("/spectral_analysis/peaks peaks", test_peaks3);
	return g_test_run(); 
}
