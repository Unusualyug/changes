# -*- coding: utf-8 -*-
"""Every entry below was resolved against Crossref (or DataCite for arXiv DOIs)
during this revision. Fields: authors (IEEE style, already formatted), title,
venue, vol, no, pp, year, doi.
"""

REFS = {
"wang2017": dict(
  a="X. Wang, Y. Peng, L. Lu, Z. Lu, M. Bagheri, and R. M. Summers",
  t="ChestX-ray8: Hospital-scale chest X-ray database and benchmarks on weakly-supervised classification and localization of common thorax diseases",
  v="Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)", pp="3462&ndash;3471", y="2017",
  doi="10.1109/CVPR.2017.369",
  note="Crossref lists pp. 3462&ndash;3471 for the IEEE proceedings version; the widely circulated open-access PDF shows 2097&ndash;2106, which is the arXiv pagination and must not be cited."),
"johnson2019": dict(
  a="A. E. W. Johnson, T. J. Pollard, S. J. Berkowitz, N. R. Greenbaum, M. P. Lungren, C.-y. Deng, R. G. Mark, and S. Horng",
  t="MIMIC-CXR, a de-identified publicly available database of chest radiographs with free-text reports",
  v="Sci. Data", vol="6", no="1", pp="Art. no. 317", y="2019",
  doi="10.1038/s41597-019-0322-0"),
"irvin2019": dict(
  a="J. Irvin, P. Rajpurkar, M. Ko, Y. Yu, S. Ciurea-Ilcus, C. Chute, H. Marklund, B. Haghgoo, R. Ball, K. Shpanskaya, J. Seekins, D. A. Mong, S. S. Halabi, J. K. Sandberg, R. Jones, D. B. Larson, C. P. Langlotz, B. N. Patel, M. P. Lungren, and A. Y. Ng",
  t="CheXpert: A large chest radiograph dataset with uncertainty labels and expert comparison",
  v="Proc. AAAI Conf. Artif. Intell.", vol="33", no="1", pp="590&ndash;597", y="2019",
  doi="10.1609/aaai.v33i01.3301590",
  note="Crossref records this entry only under the AAAI proceedings DOI. The commonly quoted CVPR 2019 DOI (10.1109/CVPR.2019.00021) does not resolve in Crossref and was therefore not used."),
"rajpurkar2018": dict(
  a="P. Rajpurkar, J. Irvin, R. L. Ball, K. Zhu, B. Yang, H. Mehta, T. Duan, D. Ding, A. Bagul, C. P. Langlotz, B. N. Patel, K. W. Yeom, K. Shpanskaya, F. G. Blankenberg, J. Seekins, T. J. Amrhein, D. A. Mong, S. S. Halabi, E. J. Zucker, A. Y. Ng, and M. P. Lungren",
  t="Deep learning for chest radiograph diagnosis: A retrospective comparison of the CheXNeXt algorithm to practicing radiologists",
  v="PLOS Med.", vol="15", no="11", pp="Art. no. e1002686", y="2018",
  doi="10.1371/journal.pmed.1002686"),
"huang2017": dict(
  a="G. Huang, Z. Liu, L. van der Maaten, and K. Q. Weinberger",
  t="Densely connected convolutional networks",
  v="Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)", pp="2261&ndash;2269", y="2017",
  doi="10.1109/CVPR.2017.243",
  note="IEEE proceedings pagination is 2261&ndash;2269; the open-access version of record is paginated 4700&ndash;4708."),
"he2016": dict(
  a="K. He, X. Zhang, S. Ren, and J. Sun",
  t="Deep residual learning for image recognition",
  v="Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)", pp="770&ndash;778", y="2016",
  doi="10.1109/CVPR.2016.90"),
"deng2009": dict(
  a="J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei",
  t="ImageNet: A large-scale hierarchical image database",
  v="Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)", pp="248&ndash;255", y="2009",
  doi="10.1109/CVPR.2009.5206848"),
"selvaraju2017": dict(
  a="R. R. Selvaraju, M. Cogswell, A. Das, R. Vedantam, D. Parikh, and D. Batra",
  t="Grad-CAM: Visual explanations from deep networks via gradient-based localization",
  v="Proc. IEEE Int. Conf. Comput. Vis. (ICCV)", pp="618&ndash;626", y="2017",
  doi="10.1109/ICCV.2017.74"),
"zhou2016": dict(
  a="B. Zhou, A. Khosla, A. Lapedriza, A. Oliva, and A. Torralba",
  t="Learning deep features for discriminative localization",
  v="Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)", pp="2921&ndash;2929", y="2016",
  doi="10.1109/CVPR.2016.319"),
"oakden2020": dict(
  a="L. Oakden-Rayner",
  t="Exploring large-scale public medical image datasets",
  v="Acad. Radiol.", vol="27", no="1", pp="106&ndash;112", y="2020",
  doi="10.1016/j.acra.2019.10.006"),
"rudin2019": dict(
  a="C. Rudin",
  t="Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead",
  v="Nature Mach. Intell.", vol="1", no="5", pp="206&ndash;215", y="2019",
  doi="10.1038/s42256-019-0048-x"),
"geirhos2020": dict(
  a="R. Geirhos, J.-H. Jacobsen, C. Michaelis, R. Zemel, W. Brendel, M. Bethge, and F. A. Wichmann",
  t="Shortcut learning in deep neural networks",
  v="Nature Mach. Intell.", vol="2", no="11", pp="665&ndash;673", y="2020",
  doi="10.1038/s42256-020-00257-z"),
"zech2018": dict(
  a="J. R. Zech, M. A. Badgeley, M. Liu, A. B. Costa, J. J. Titano, and E. K. Oermann",
  t="Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study",
  v="PLOS Med.", vol="15", no="11", pp="Art. no. e1002683", y="2018",
  doi="10.1371/journal.pmed.1002683"),
"karimi2020": dict(
  a="D. Karimi, H. Dou, S. K. Warfield, and A. Gholipour",
  t="Deep learning with noisy labels: Exploring techniques and remedies in medical image analysis",
  v="Med. Image Anal.", vol="65", pp="Art. no. 101759", y="2020",
  doi="10.1016/j.media.2020.101759"),
"vanCalster2019": dict(
  a="B. Van Calster, D. J. McLernon, M. van Smeden, L. Wynants, and E. W. Steyerberg",
  t="Calibration: The Achilles heel of predictive analytics",
  v="BMC Med.", vol="17", no="1", pp="Art. no. 230", y="2019",
  doi="10.1186/s12916-019-1466-7"),
"seyyed2021": dict(
  a="L. Seyyed-Kalantari, H. Zhang, M. B. A. McDermott, I. Y. Chen, and M. Ghassemi",
  t="Underdiagnosis bias of artificial intelligence algorithms applied to chest radiographs in under-served patient populations",
  v="Nature Med.", vol="27", no="12", pp="2176&ndash;2182", y="2021",
  doi="10.1038/s41591-021-01595-0"),
"larrazabal2020": dict(
  a="A. J. Larrazabal, N. Nieto, V. Peterson, D. H. Milone, and E. Ferrante",
  t="Gender imbalance in medical imaging datasets produces biased classifiers for computer-aided diagnosis",
  v="Proc. Nat. Acad. Sci. USA", vol="117", no="23", pp="12592&ndash;12594", y="2020",
  doi="10.1073/pnas.1919012117"),
"obermeyer2019": dict(
  a="Z. Obermeyer, B. Powers, C. Vogeli, and S. Mullainathan",
  t="Dissecting racial bias in an algorithm used to manage the health of populations",
  v="Science", vol="366", no="6464", pp="447&ndash;453", y="2019",
  doi="10.1126/science.aax2342"),
"gichoya2022": dict(
  a="J. W. Gichoya, I. Banerjee, A. R. Bhimireddy, J. L. Burns, L. A. Celi, L.-C. Chen, R. Correa, N. Dullerud, M. Ghassemi, S.-C. Huang, P.-C. Kuo, M. P. Lungren, L. J. Palmer, B. J. Price, S. Purkayastha, A. T. Pyrros, L. Oakden-Rayner, C. Okechukwu, L. Seyyed-Kalantari, H. Trivedi, R. Wang, Z. Zaiman, and H. Zhang",
  t="AI recognition of patient race in medical imaging: A modelling study",
  v="Lancet Digit. Health", vol="4", no="6", pp="e406&ndash;e414", y="2022",
  doi="10.1016/S2589-7500(22)00063-2"),
"baltru2019": dict(
  a="T. Baltrusaitis, C. Ahuja, and L.-P. Morency",
  t="Multimodal machine learning: A survey and taxonomy",
  v="IEEE Trans. Pattern Anal. Mach. Intell.", vol="41", no="2", pp="423&ndash;443", y="2019",
  doi="10.1109/TPAMI.2018.2798607"),
"huang2020": dict(
  a="S.-C. Huang, A. Pareek, S. Seyyedi, I. Banerjee, and M. P. Lungren",
  t="Fusion of medical imaging and electronic health records using deep learning: A systematic review and implementation guidelines",
  v="npj Digit. Med.", vol="3", no="1", pp="Art. no. 136", y="2020",
  doi="10.1038/s41746-020-00341-z"),
"kermany2018": dict(
  a="D. S. Kermany, M. Goldbaum, W. Cai, C. C. S. Valentim, H. Liang, S. L. Baxter, A. McKeown, G. Yang, X. Wu, F. Yan, J. Dong, M. K. Prasadha, J. Pei, M. Y. L. Ting, J. Zhu, C. Li, S. Hewett, J. Dong, I. Ziyar, A. Shi, R. Zhang, L. Zheng, R. Hou, W. Shi, X. Fu, Y. Duan, V. A. N. Huu, C. Wen, E. D. Zhang, C. L. Zhang, O. Li, X. Wang, M. A. Singer, X. Sun, J. Xu, A. Tafreshi, M. A. Lewis, H. Xia, and K. Zhang",
  t="Identifying medical diagnoses and treatable diseases by image-based deep learning",
  v="Cell", vol="172", no="5", pp="1122&ndash;1131.e9", y="2018",
  doi="10.1016/j.cell.2018.02.010"),
"loshchilov2019": dict(
  a="I. Loshchilov and F. Hutter",
  t="Decoupled weight decay regularization",
  v="Proc. Int. Conf. Learn. Represent. (ICLR)", y="2019",
  doi="10.48550/arXiv.1711.05101"),
"paszke2019": dict(
  a="A. Paszke, S. Gross, F. Massa, A. Lerer, J. Bradbury, G. Chanan, T. Killeen, Z. Lin, N. Gimelshein, L. Antiga, A. Desmaison, A. K&ouml;pf, E. Yang, Z. DeVito, M. Raison, A. Tejani, S. Chilamkurthy, B. Steiner, L. Fang, J. Bai, and S. Chintala",
  t="PyTorch: An imperative style, high-performance deep learning library",
  v="Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)", vol="32", pp="8024&ndash;8035", y="2019",
  doi="10.48550/arXiv.1912.01703"),
"efron1994": dict(
  a="B. Efron and R. J. Tibshirani",
  t="An Introduction to the Bootstrap", v="New York, NY, USA: Chapman &amp; Hall/CRC", y="1994",
  doi="10.1201/9780429246593"),
}
