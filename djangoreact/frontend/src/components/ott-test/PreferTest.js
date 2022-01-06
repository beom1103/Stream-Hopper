import React, { useState, useCallback, useEffect } from "react";
import { useRecoilValue, useRecoilState } from "recoil";
import { genreTopMovie } from "../../api/api";
import { ottTestAtom } from "../../store/testStore";
import { Link } from "react-router-dom";

const PreferTest = () => {
  const topGenreMovie = useRecoilValue(genreTopMovie);
  const [testData, setTestData] = useRecoilState(ottTestAtom);
  const [movieList, setMovieList] = useState([]);

  const handleMovieList = useCallback(
    (e) => {
      const value = e.target.value;
      if (movieList.length >= 3) {
        alert("최대 3개 까지만 선택해주세요.");
        e.target.checked = false;
      }
      let newData = movieList.filter((item) => item !== value);
      if (e.target.checked) newData.push(value);
      setMovieList(newData);
    },
    [movieList]
  );

  useEffect(() => {
    setTestData({ ...testData, prefer_contents: movieList });
  }, [movieList]);

  return (
    <div>
      <div className="movie-box">
        <h3>좋아하시는 영화를 선택하세요.(총 3개)</h3>
        <h4>{movieList.length} / 3</h4>
        <div className="row row-cols-4 row-cols-sm-6 row-cols-md-6">
          {topGenreMovie.map((movie, idx) => {
            const newData = {};
            newData[idx] = movie;
            const korImg = newData[idx].kor_image_path;
            const originalImg = newData[idx].image_path;
            return (
              <div key={"contents" + idx} className="col">
                <input
                  id={newData[idx].id}
                  type="checkbox"
                  value={newData[idx].id}
                  onClick={handleMovieList}
                />
                <label value={newData[idx].id} htmlFor={newData[idx].id}>
                  ❤
                </label>
                <img
                  name="prefer_contents"
                  src={`https://image.tmdb.org/t/p/original${
                    korImg || originalImg || null
                  } `}
                  alt="selectMovie"
                  className="img-fluid card-img-top"
                />
              </div>
            );
          })}
        </div>
      </div>
      {movieList.length === 3 && (
        <Link to="/ott_result">
          <button>제출</button>
        </Link>
      )}
    </div>
  );
};

export default PreferTest;