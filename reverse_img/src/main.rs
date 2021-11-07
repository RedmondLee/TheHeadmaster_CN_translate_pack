use std::{env, fs};
use std::path::Path;
use std::ffi::OsStr;
use std::io::prelude::*;

// 目前没有做目录递归，只处理顶层目录。

fn splitext(filename: &str) -> Option<&str> {
    Path::new(filename)
        .extension()
        .and_then(OsStr::to_str)
}

fn treat_dir(
    watch_list: &Vec<&str>,
    watch_header: &Vec<[u8; 4]>,
    enc_flag: bool,
    s_dir_str: String,
) {
    let paths = fs::read_dir(s_dir_str).unwrap();
    for path in paths {
        let path_str = path.unwrap().path().into_os_string().into_string().unwrap();
        let md = fs::metadata(&path_str).unwrap();
        if md.is_dir() {
            treat_dir(watch_list, watch_header, enc_flag, path_str);
            continue;
        }
        let ext = splitext(&*path_str).unwrap().to_lowercase();
        if watch_list.contains(&&*ext) {
            // 文件扩展名存在于监视列表中
            let mut f = fs::File::open(&path_str).expect("Something went wrong reading the file");
            let mut buf: Vec<u8> = vec![0; 20971520];
            let n:usize = f.read(&mut buf[..]).unwrap();
            if (n > 4) && (watch_header.contains(&buf[..4].try_into().expect("slice with incorrect length"))){
                // 是正文件
                if enc_flag {
                    // 编码
                    let mut reversed: Vec<u8> = vec![];
                    reversed.extend(buf[..n].iter().rev());
                    let mut file = fs::File::create(path_str).unwrap();
                    file.write_all(&reversed);
                }
            } else {
                // 是反文件
                if !enc_flag {
                    // 解码
                    let mut reversed: Vec<u8> = vec![];
                    reversed.extend(buf[..n].iter().rev());
                    let mut file = fs::File::create(path_str).unwrap();
                    file.write_all(&reversed);
                }
            }
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let enc_str: String = String::from("--enc");
    let dec_str: String = String::from("--dec");
    let help_str: String = String::from("-h");
    let mut enc_flag = false;
    if args.len() > 1 {
        if enc_str.eq(&args[1]) {
            enc_flag = true;
        } else if dec_str.eq(&args[1]) {
            enc_flag = false;
        } else if help_str.eq(&args[1]) {
            println!("Help: todo.");
            return ();
        }
    }

    let watch_list: Vec<&str> = vec!["png","jpg","jpeg","bmp","webp","txt"];
    let watch_header: Vec<[u8; 4]> = vec![
        [255, 216, 255, 225],
        [255, 216, 255, 224], 
        [255, 216, 255, 219],
        [82, 73, 70, 70],
        [137, 80, 78, 71]
    ];
    
    let s_dir_str = String::from(".\\images");
    treat_dir(&watch_list, &watch_header, enc_flag, s_dir_str);
}
