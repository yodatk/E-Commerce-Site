import React, {Component} from "react";
import {
    MDBBtn,
    MDBCol,
    MDBContainer,
    MDBIcon,
    MDBInput,
    MDBNavbarBrand, MDBNavItem, MDBNavLink,
    MDBRow,
    MDBTable,
    MDBTableBody,
    MDBTableHead, MDBTooltip
} from "mdbreact";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes";
import {Redirect} from "react-router-dom";
import PropTypes from "prop-types";

export class SearchStoresPage extends Component {
    state = {
        storename: null,
        errors: FormUtils.defaultSearchStoresDictionary(),
        been_submitted: false,
        search_result: [],
        msg: "",
        redirectAddress: null
    };
    formUtils = new FormUtils();


    validateStoreName = () => this.formUtils.validate_storeName_for_search(this.state.storename, this.state.errors);

    onChange = (e) => {
        if ((this.state.storename === null) || ((e.target.name === "storename") && (e.target.value.trim() !== this.state.storename.trim()))) {
            this.setState({[e.target.name]: e.target.value}, this.handleNewSearch);
        } else {
            this.setState({[e.target.name]: e.target.value});
        }

    }
    clearErrors = () => {
        this.setState({errors: FormUtils.defaultSearchStoresDictionary()})
    }
    sendIfPossible = () => {
        if (this.state.errors["is_valid"]) {
            axios.get(
                `/search_for_stores`,
                {
                    params: {
                        user_id: this.props.getUserId.bind(this)(),
                        store_name: this.state.storename.trim()
                    }
                }
            )

                .then((res) => {
                    console.log(res)
                    // this.props.updateParent.bind(this)(res)
                    this.dealWithSearchResult(res);
                }).catch(error => {
                console.log(error)
                this.dealWithSearchResult(error.response);
            });
        }
    }

    updateSearchResults = (res) => {
        this.setState({search_result: res.data["stores"]})
        console.log(res.data)
    }

    dealWithSearchResult = (res) => {
        if (res) {
            if (res.status === HttpStatus.OK) {
                this.updateSearchResults(res);
                if (this.props.getUserId() === -1) {
                    this.props.updateParent(res)
                }
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }
    };

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ");
            msg = msg.split("_").join(" ");
            return msg;
        }
    }


    handleNewSearch = () => {
        this.clearErrors();
        let new_errors = this.formUtils.validate_store_search(this.state.storename);
        if (new_errors["is_valid"]) {
            this.setState({
                    been_submitted: true,
                    errors: new_errors
                },
                this.sendIfPossible);
        }
    }

    onSubmit = (e) => {
        e.preventDefault();
        this.handleNewSearch();
    }
    // changeAddress = () => {
    //     //todo -> change to view store / store_name
    //     this.setState({redirectAddress: "/"})
    // }


    renderResults = () => {
        if (!this.state.been_submitted) {
            this.setState({storename: "", been_submitted: true}, this.handleNewSearch)
        }
        return <MDBContainer>
            <MDBTable responsive>
                <MDBTableHead color="default-color" textWhite>
                    <tr>
                        <th>#</th>
                        <th>Store name</th>
                        <th>Creation Date</th>
                        <th>Link</th>
                    </tr>
                </MDBTableHead>
                <MDBTableBody>
                    {this.state.search_result.map((store, i) => (
                        <tr>
                            <td>{i + 1}</td>
                            <td>{store.name}</td>
                            <td>{store.creation_date}</td>
                            <td><MDBNavLink to={`/store_page/${store.name}`}><MDBIcon icon="store"/></MDBNavLink></td>
                        </tr>
                    ))}
                </MDBTableBody>
            </MDBTable>
        </MDBContainer>
    }


    render() {
        if (this.state.redirectAddress != null) {
            return <Redirect to={this.state.redirectAddress}/>
        }
        return (
            <React.Fragment>
                <MDBContainer style={{padding: "10px"}}>
                    <MDBRow
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}>
                        <MDBCol md="6">
                            <form className="needs-validation" onSubmit={this.onSubmit} noValidate>
                                <p onChange={this.onChange} className="h3 text-center mb-4">Search Stores</p>
                                <div className="grey-text">
                                    <div className="form-group">
                                        <MDBInput onChange={this.onChange} value={this.state.storename}
                                                  name="storename"
                                                  label="Store name" icon="store" group type="text"
                                                  id="defaultFormRegisterNameEx"
                                                  className={this.state.been_submitted ? (this.validateStoreName() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                  required
                                                  error="wrong"
                                                  success="right"/>
                                        <div className="invalid-feedback"
                                             style={{display: "block"}}>{this.state.errors["storename"]}</div>
                                        <div className="valid-feedback"/>
                                    </div>
                                </div>
                            </form>
                            <p onChange={this.onChange}
                               className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                        </MDBCol>
                    </MDBRow>
                    <MDBRow>
                        {this.renderResults()}
                    </MDBRow>
                </MDBContainer>
            </React.Fragment>
        );
    }
}

// PropTypes
SearchStoresPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserId: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
};


export default SearchStoresPage;